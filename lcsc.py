import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

def main():
    base_dir = Path.cwd();
    if (base_dir / "lcsc.txt").is_file():
        input_file = base_dir / "lcsc.txt"
    else:
        print("Error cannot find file.")
        return 1
    with open(input_file, "r", encoding="utf-8") as f:
        ids = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]
    ids = list(dict.fromkeys(ids))
    if not ids:
        print("no ids found")
        return 0
    symbols_dir = base_dir / "symbols"
    footprints_dir = base_dir / "footprints"
    
    symbols_dir.mkdir(exist_ok=True)
    footprints_dir.mkdir(exist_ok=True)
    
    symbol_file = symbols_dir / "lcsc.kicad_sym"
    footprint_lib = footprints_dir / "lcsc.pretty"
    
    python_exec = sys.executable
    
    print(f"Found {len(ids)} lcsc ids")
    with tempfile.TemporaryDirectory(dir=base_dir) as temp:
        temp = Path(temp)
        
        output = temp / "library"
        temp_symbol = temp / "library.kicad_sym"
        temp_footprints = temp / "library.pretty"
        
        if symbol_file.exists():
            shutil.copy2(symbol_file, temp_symbol)
        if footprint_lib.exists():
            shutil.copytree(footprint_lib, temp_footprints)
        else:
            temp_footprints.mkdir()
        failed = []
        
        for i, lcsc_id in enumerate(ids, start=1):
            cmd = [
                python_exec,
                "-m", "easyeda2kicad",
                "--symbol",
                "--footprint",
                "--overwrite",
                f"--lcsc_id={lcsc_id}",
                f"--output={output}",
            ]
            print(f"[{i}/{len(ids)}] Processing {lcsc_id}")
            try:
                subprocess.run(cmd, check=True)
                print(f"Done: {lcsc_id}\n")
            except subprocess.CalledProcessError:
                print(f"Failed: {lcsc_id}\n")
                failed.append(lcsc_id)
            except FileNotFoundError:
                print("error: python executable not found")
                return 1
        if temp_symbol.exists():
            shutil.copy2(temp_symbol, symbol_file)
        if temp_footprints.exists():
            if footprint_lib.exists():
                shutil.rmtree(footprint_lib)
            shutil.move(str(temp_footprints), str(footprint_lib))
    print("Conversion done")
    print(f"Symbols: {symbol_file}")
    print(f"Footprints: {footprint_lib}")
    
    if failed:
        print(f"\nFailed to convert {len(failed)}")
        for part in failed:
            print(f" - {part}")
        return 1
    print("all components converted")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
