import os
import sys

from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from functools import partial
from math import ceil
from logging import basicConfig, INFO, info, debug
from pathlib import Path
from shlex import quote
from shutil import move
from tempfile import TemporaryDirectory
from textwrap import dedent
from timeit import timeit
from typing import Callable

import matplotlib.pyplot as plt

from Bio.SeqIO import parse, write
from pandas import DataFrame, Index

basicConfig(level=INFO, format='%(levelname)s: %(message)s')

PROJ_ROOT = Path(__file__).parent.parent.parent

ins = PROJ_ROOT / "assets/ins.fa"
pol = PROJ_ROOT / "assets/pol.fa"
img = PROJ_ROOT / "assets/img"
prof = PROJ_ROOT / "assets/profiling"


def parse_args(args: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description="Script for profiling time and space complexity of the developed aligner.")

    parser.add_argument("-u", "--update", action="store_true", help="update cabals package list before building the executable")
    parser.add_argument("-b", "--build-dir", default="build", help="name of the build dir to be created in the project root")
    parser.add_argument("-t", "--skip-time", dest="profile_time", action="store_false", help="skip analysis of time complexity")
    parser.add_argument("-s", "--skip-space", dest="profile_space", action="store_false", help="skip analysis of space complexity")
    parser.add_argument("-i", "--skip-ins", dest="dump_ins", action="store_false", help="don't use ins.fa for memory profiling")
    parser.add_argument("-l", "--seqlen", type=int, default=150, help="length of pol.fa subsequence used for memory profiling")

    if args is None:
        args = sys.argv[1:]

    return parser.parse_args(args)


def main(args: list[str] | None = None):
    args = parse_args(args)
    exe = build_project(args.build_dir, args.update)

    with TemporaryDirectory() as dir_name:
        tmp_dir = Path(dir_name)
        try:
            if args.profile_time:
                time_analysis(exe, tmp_dir)
            if args.profile_space:
                space_analysis(exe, tmp_dir, args)
        except KeyboardInterrupt:
            info("Aborted execution")


@contextmanager
def directory(dir: str | Path | None = None):
    # enter dir as context manager
    if dir is None:
        dir = PROJ_ROOT
    dir = Path(dir).resolve()

    cwd = os.getcwd()
    try:
        debug((f"Left {cwd}"))
        os.chdir(dir)
        yield dir
    finally:
        os.chdir(cwd)


def update_pkg_list():
    rtn = os.system("cabal update")
    if rtn != 0:
        raise RuntimeError("Couldn't update package list")


def build_project(build_dir_name: str = "build.prof", update: bool = False) -> Path:
    # build executable
    if update:
        update_pkg_list()

    with directory():
        build_dir = PROJ_ROOT / build_dir_name
        rtn = os.system(f"cabal build -j --enable-profiling --builddir={quote(str(build_dir))}")
        exe = next((path for path in build_dir.glob("**/seafovl") if path.is_file()), None)
    
    if rtn != 0:
        raise RuntimeError("Couldn't compile project. Have you installed GHC with profiling? (ghc-prof)")
    
    if exe is None:
        raise RuntimeError("Couldn't find executable")

    return exe.resolve()


def get_head(tmp_dir: Path, fasta: Path, count: int) -> Path:
    # create fasta with first n symbols per seq
    seqs = parse(fasta, "fasta")
    part_file = tmp_dir / f"{fasta.stem}_{count}.fa"
    partial_seqs = [seq[:count] for seq in seqs]
    write(partial_seqs, part_file, "fasta")
    return part_file


def prepare_parts(fasta: Path,
                  tmp_dir: Path,
                  max_syms: int | None = None,
                  steps: int = 10) -> dict[int, Path]:
    # prepare sample sequences of differing lengths
    seq1, seq2 = parse(fasta, "fasta")
    
    if max_syms is None:
        max_syms = min(len(seq1), len(seq2))

    step_size = max_syms // steps
    symbol_counts = [1, *((i+1) * step_size for i in range(steps))]

    return {count: get_head(tmp_dir, fasta, count) for count in symbol_counts}


def get_cmd(exe_path: str | Path, fasta_path: str | Path):
    exe = quote(str(exe_path))
    fasta = quote(str(fasta_path))
    return f"{exe} {fasta} 20 1 -1 -2"


def align(fasta: Path, *, exe: Path) -> dict:
    cmd = f"{get_cmd(exe, fasta)} > /dev/null"
    return {"stmt": lambda: os.system(cmd)}


def get_bp_args(fasta: Path) -> dict:
    setup = dedent(f"""
    from Bio.Align import PairwiseAligner
    from Bio.SeqIO import parse

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 1
    aligner.mismatch_score = -1
    aligner.open_gap_score = -2
    aligner.extend_gap_score = -2
    
    hiv, siv = parse("{quote(str(fasta))}", "fasta")
    """)

    return {"stmt": "aligner.align(hiv, siv)", "setup": setup}


def process(files: dict[int, Path], methods: dict[str, Callable[[Path], dict]]) -> DataFrame:
    data = []
    with directory():
        for i, (n, file) in enumerate(files.items()):
            n_times = []
            for name, kwarg_getter in methods.items():
                kwargs = {**kwarg_getter(file), "number": 1}
                time = timeit(**kwargs)
                n_times.append(time)

            datum = (n, n_times)
            data.append(datum)
            info(f"Processed {i+1} of {len(files)} files")
    
    # data: list[tuple[int, tuple[float, float]]]
    counts, times = zip(*data)
    index = Index(counts, name="Bases")
    cols = list(methods.keys()) 
    return DataFrame(times, index=index, columns=cols)


def save_plot(data: DataFrame, svg_out: Path, title: str):
    xlim = data.index.min(), data.index.max()
    max_t = data.max().max()
    secs = ceil(max_t * 100) / 100
    ylim = 0, secs
    data.plot(title=title, ylabel="seconds", xlim=xlim, ylim=ylim)
    plt.savefig(svg_out, format="svg")
    info(f"Saved graph to {svg_out}")


def time_analysis(exe: Path, tmp_dir: Path):
    # prepare executable and timing functions
    get_hs_args = partial(align, exe=exe)

    hs, bp = {"Haskell": get_hs_args}, {"Biopython": get_bp_args}
    methods = {**hs, **bp}

    # align ins with both methods
    info("Aligning ins.fa with Haskell and Biopython")
    ins_files = prepare_parts(ins, tmp_dir, steps=25)
    ins_data = process(ins_files, methods)

    # align pol with biopython only
    info("Aligning pol.fa with Biopython")
    pol_files = prepare_parts(pol, tmp_dir, steps=25)
    pol_data = process(pol_files, bp)
    
    # save data
    info("Saving timing data")
    ins_data.to_csv(prof / "aln_timing_ins.csv")
    pol_data.to_csv(prof / "aln_timing_pol.csv")

    # save graphs
    info("Generating graphs")
    save_plot(ins_data, svg_out=img / "aln_timing_ins.svg", title=r"Haskell vs. Biopython on fragments of $\mathtt{assets/ins.fa}$")
    save_plot(pol_data, svg_out=img / "aln_timing_pol.svg", title=r"Biopython on fragments of $\mathtt{assets/pol.fa}$")


def create_heap_dump(exe: Path, fasta: Path) -> Path:
    rts_opts = f"+RTS -hy -pa -l -RTS"
    cmd = f"{get_cmd(exe, fasta)} {rts_opts} > /dev/null"
    with directory(prof):
        info(f"Creating heap dump for {fasta.stem}.")
        rtn = os.system(cmd)
        if rtn != 0:
            raise RuntimeError("Couldn't create heap dump")
        dump_loc = Path(exe.stem + '.eventlog')
        if not dump_loc.is_file():
            raise RuntimeError("Can't find prof heap dump.")
        dump_dest = Path(fasta.stem + '.eventlog').resolve()
        move(dump_loc, dump_dest)

    info(f"Wrote heap dump to {dump_dest.relative_to(PROJ_ROOT)}")
    return dump_dest

def render_dump(dump: Path):
    with directory(prof):
        # print with profile 1
        os.system(f"hp2ps -c {quote(str(dump))}")
        ps = Path(dump.stem + ".ps")
        img_dest = quote(str(img / (dump.stem + ".svg")))
        os.system(f"inkscape -D -l -o {img_dest} {quote(str(ps))}")
        ps.unlink()

        # print with profile 2
        os.system(f"hp2ps -p -c -m0 {quote(str(dump))}")
        ps = Path(dump.stem + ".ps")
        img_dest = quote(str(img / (dump.stem + "_fine.svg")))
        os.system(f"inkscape -D -l -o {img_dest} {quote(str(ps))}")
        ps.unlink()

        aux = Path(dump.stem + ".aux")
        aux.unlink()

def space_analysis(exe: Path, tmp_dir: Path, args: Namespace):
    pol_part = get_head(tmp_dir, pol, args.seqlen)
    dump = create_heap_dump(exe, pol_part)
    # render_dump(dump)

    if args.dump_ins:
        dump = create_heap_dump(exe, ins)
        # render_dump(dump)


if __name__ == "__main__":
    main()
