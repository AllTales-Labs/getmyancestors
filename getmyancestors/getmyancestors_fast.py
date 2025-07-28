#!/usr/bin/env python3
"""
Ultra-fast version of getmyancestors that only extracts essential data:
- Name
- Birth/death dates and locations
- Profile ID
- Family relationships
- No sources, no notes, no memories
"""

import sys
import time
import re
import getpass
import argparse
from getmyancestors.classes.tree_ultra_fast import Tree
from getmyancestors.classes.session import Session

def main():
    parser = argparse.ArgumentParser(
        description="Ultra-fast GEDCOM extraction from FamilySearch (minimal data)",
        add_help=False,
        usage="getmyancestors_fast -u username -p password [options]",
    )
    parser.add_argument(
        "-u", "--username", metavar="<STR>", type=str, help="FamilySearch username"
    )
    parser.add_argument(
        "-p", "--password", metavar="<STR>", type=str, help="FamilySearch password"
    )
    parser.add_argument(
        "-i",
        "--individuals",
        metavar="<STR>",
        nargs="+",
        type=str,
        help="List of individual FamilySearch IDs for whom to retrieve ancestors",
    )
    parser.add_argument(
        "-a",
        "--ascend",
        metavar="<INT>",
        type=int,
        default=4,
        help="Number of generations to ascend [4]",
    )
    parser.add_argument(
        "-d",
        "--descend",
        metavar="<INT>",
        type=int,
        default=0,
        help="Number of generations to descend [0]",
    )
    parser.add_argument(
        "-m",
        "--marriage",
        action="store_true",
        default=False,
        help="Add spouses and couples information [False]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Increase output verbosity [False]",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        metavar="<INT>",
        type=int,
        default=60,
        help="Timeout in seconds [60]",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        metavar="<FILE>",
        type=argparse.FileType("w", encoding="UTF-8"),
        default=sys.stdout,
        help="output GEDCOM file [stdout]",
    )
    parser.add_argument(
        "-l",
        "--logfile",
        metavar="<FILE>",
        type=argparse.FileType("w", encoding="UTF-8"),
        default=False,
        help="output log file [stderr]",
    )

    try:
        parser.error = parser.exit
        args = parser.parse_args()
    except SystemExit:
        parser.print_help(file=sys.stderr)
        sys.exit(2)

    if args.individuals:
        for fid in args.individuals:
            if not re.match(r"[A-Z0-9]{4}-[A-Z0-9]{3}", fid):
                sys.exit("Invalid FamilySearch ID: " + fid)

    args.username = (
        args.username if args.username else input("Enter FamilySearch username: ")
    )
    args.password = (
        args.password
        if args.password
        else getpass.getpass("Enter FamilySearch password: ")
    )

    start_time = time.time()
    timing_data = {
        'login': 0,
        'starting_individuals': 0,
        'ancestors': 0,
        'descendants': 0,
        'spouses': 0,
        'total': 0
    }

    # Login
    login_start = time.time()
    print("Login to FamilySearch...", file=sys.stderr)
    fs = Session(
        args.username,
        args.password,
        verbose=args.verbose,
        logfile=args.logfile,
        timeout=args.timeout,
    )
    if not fs.logged:
        sys.exit(2)
    timing_data['login'] = time.time() - login_start
    _ = fs._
    tree = Tree(fs)

    try:
        # Starting individuals
        todo = args.individuals if args.individuals else [fs.fid]
        starting_start = time.time()
        print(_("Downloading starting individuals..."), file=sys.stderr)
        tree.add_indis(todo)
        timing_data['starting_individuals'] = time.time() - starting_start

        # Ancestors
        ancestors_start = time.time()
        todo = set(tree.indi.keys())
        done = set()
        for i in range(args.ascend):
            if not todo:
                break
            done |= todo
            print(
                _("Downloading %s. of generations of ancestors...") % (i + 1),
                file=sys.stderr,
            )
            todo = tree.add_parents(todo) - done
        timing_data['ancestors'] = time.time() - ancestors_start

        # Descendants
        descendants_start = time.time()
        todo = set(tree.indi.keys())
        done = set()
        for i in range(args.descend):
            if not todo:
                break
            done |= todo
            print(
                _("Downloading %s. of generations of descendants...") % (i + 1),
                file=sys.stderr,
            )
            todo = tree.add_children(todo) - done
        timing_data['descendants'] = time.time() - descendants_start

        # Spouses
        if args.marriage:
            spouses_start = time.time()
            print(_("Downloading spouses and marriage information..."), file=sys.stderr)
            todo = set(tree.indi.keys())
            tree.add_spouses(todo)
            timing_data['spouses'] = time.time() - spouses_start

    finally:
        # Generate GEDCOM
        tree.reset_num()
        tree.print(args.outfile)
        timing_data['total'] = time.time() - start_time
        
        print(
            _(
                "Downloaded %s individuals, %s families, %s sources and %s notes "
                "in %s seconds with %s HTTP requests."
            )
            % (
                str(len(tree.indi)),
                str(len(tree.fam)),
                str(len(tree.sources)),
                str(len(tree.notes)),
                str(round(timing_data['total'])),
                str(fs.counter),
            ),
            file=sys.stderr,
        )
        
        # Print detailed timing information
        print("\n=== ULTRA-FAST TIMING BREAKDOWN ===", file=sys.stderr)
        print(f"Login: {timing_data['login']:.2f}s", file=sys.stderr)
        print(f"Starting individuals: {timing_data['starting_individuals']:.2f}s", file=sys.stderr)
        print(f"Ancestors: {timing_data['ancestors']:.2f}s", file=sys.stderr)
        print(f"Descendants: {timing_data['descendants']:.2f}s", file=sys.stderr)
        print(f"Spouses: {timing_data['spouses']:.2f}s", file=sys.stderr)
        print(f"Total: {timing_data['total']:.2f}s", file=sys.stderr)
        print(f"HTTP requests: {fs.counter}", file=sys.stderr)
        print(f"Requests per second: {fs.counter/timing_data['total']:.1f}", file=sys.stderr)
        print(f"Individuals per second: {len(tree.indi)/timing_data['total']:.1f}", file=sys.stderr)

if __name__ == "__main__":
    main() 