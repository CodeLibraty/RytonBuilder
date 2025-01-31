from pathlib import Path
import subprocess
import shutil
import json
import os

class RytonBuilder:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.build_path = self.project_path / 'build'
        self.cache_path = self.project_path / '.ryton_cache'
        
        # Создаем директории
        self.build_path.mkdir(exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)

    def find_ryton_installation(self):
        # Поиск установленного Ryton
        paths = [
            '/usr/local/lib/ryton',
            '/usr/lib/ryton',
            os.path.expanduser('~/.local/lib/ryton'),
            os.path.expanduser('~/ryton')
        ]
        
        for path in paths:
            if Path(path).exists():
                return Path(path)
        return None

    def cache_sources(self, main_file: str):
        # Кэшируем исходники проекта
        cache_file = self.cache_path / 'sources.json'
        sources = {}
        
        # Рекурсивно собираем все .ry файлы
        for file in self.project_path.rglob('*.ry'):
            relative_path = file.relative_to(self.project_path)
            sources[str(relative_path)] = file.read_text()
            
        with open(cache_file, 'w') as f:
            json.dump(sources, f)
            
        return cache_file

    def build(self, main_file: str, output_name: str, verbose=True):
        if verbose:
            print(f"Project path: {self.project_path}")
            print(f"Build path: {self.build_path}")
            
        # Проверяем входной файл
        main_file_path = Path(main_file)
        if not main_file_path.exists():
            print(f"Error: Main file {main_file} not found")
            return False
            
        ryton_path = self.find_ryton_installation()
        if verbose:
            print(f"Searching Ryton in: {[p for p in self.search_paths]}")
            print(f"Found Ryton: {ryton_path}")
        
        if not ryton_path:
            print("Error: Ryton installation not found")
            return False
            
        # Проверяем что это действительно Ryton
        if not (ryton_path / 'Core.py').exists():
            print(f"Error: Invalid Ryton installation at {ryton_path}")
            return False

        print("Starting Ryton project build...")
        
        ryton_path = self.find_ryton_installation()
        if not ryton_path:
            print("Error: Ryton installation not found")
            return False
        print(f"Found Ryton at: {ryton_path}")
        
        print("Caching source files...")    
        cache_file = self.cache_sources(main_file)
        
        print("Copying Ryton environment...")
        shutil.copytree(ryton_path, self.build_path / 'RytonLang', dirs_exist_ok=True)
        
        print("Creating entry point...")
        entry = f"""
    import os
    import json
    from RytonLang.Core import SharpyLang

    def main():
        with open('{cache_file}') as f:
            sources = json.load(f)
        core = SharpyLang(os.getcwd())
        core.run(sources['{main_file}'])

    if __name__ == '__main__':
        main()
    """
        entry_file = self.build_path / 'main.py'
        entry_file.write_text(entry)
        
        print("Compiling binary...")
        result = subprocess.run([
            'python3', '-m', 'nuitka',
            '--follow-imports',
            '--include-package=RytonLang',
            '--include-data-file=' + str(cache_file) + '=' + str(cache_file),
            '--static-libpython=no',
            '--output-dir=' + str(self.build_path),
            '--output-filename=' + output_name,
            str(entry_file)
        ])
        
        if result.returncode == 0:
            print(f"Build successful! Binary created at: {self.build_path}/{output_name}")
            return True
        else:
            print("Build failed!")
            return False

