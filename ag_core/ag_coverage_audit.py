import os
import ast
import glob
import re

class CoverageAuditor:
    """
    gstack 风格的 Code Path Coverage Watchdog (Python 版)
    生成代码分支的 ASCII 覆盖图，检测缺失的测试。
    """
    def __init__(self, project_cwd):
        self.cwd = project_cwd
        self.test_files_content = {}
        self._load_tests()

    def _load_tests(self):
        """预加载所有测试文件的内容用于快速匹配"""
        test_patterns = ["test_*.py", "*_test.py", "tests/**/*.py"]
        for pattern in test_patterns:
            for path in glob.glob(os.path.join(self.cwd, "**", pattern), recursive=True):
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        self.test_files_content[path] = f.read()

    def audit_file(self, target_file):
        if not target_file.endswith(".py"):
            return None
        
        path = os.path.join(self.cwd, target_file)
        if not os.path.exists(path):
            return None
            
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None

        report = [f"CODE PATH COVERAGE"]
        report.append("===========================")
        report.append(f"[+] {target_file}")
        report.append("    │")
        
        total_branches = 0
        tested_branches = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                # Check if function is tested
                is_called = any(func_name in content for content in self.test_files_content.values())
                
                # Analyze branches within function
                branches = []
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if isinstance(child, ast.If):
                        branches.append('if')
                    elif isinstance(child, ast.Try):
                        branches.append('try/except')
                    elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                        branches.append('loop')
                        
                report.append(f"    ├── {func_name}()")
                
                if not branches:
                    total_branches += 1
                    if is_called:
                        tested_branches += 1
                        report.append(f"    │   ├── [★★★ TESTED] Basic execution path")
                    else:
                        report.append(f"    │   └── [GAP]        No tests found")
                else:
                    total_branches += len(branches) + 1
                    if is_called:
                        tested_branches += 1  # count happy path
                        report.append(f"    │   ├── [★★★ TESTED] Happy path")
                        for i, branch in enumerate(branches):
                            symbol = "└──" if i == len(branches) - 1 else "├──"
                            report.append(f"    │   {symbol} [GAP]        {branch} branch — NO TEST")
                    else:
                        report.append(f"    │   └── [GAP]        Entire function unchecked")
                        
        coverage_pct = (tested_branches / total_branches * 100) if total_branches > 0 else 100
        
        report.append("")
        report.append(f"COVERAGE: {tested_branches}/{total_branches} paths tested ({coverage_pct:.0f}%)")
        if coverage_pct < 60:
            report.append("STATUS:   FAILED (Coverage < 60%)")
        else:
            report.append("STATUS:   PASS")
            
        return "\n".join(report)

if __name__ == "__main__":
    import sys
    proj_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    auditor = CoverageAuditor(proj_dir)
    target = sys.argv[2] if len(sys.argv) > 2 else "ag_core/middleware.py"
    print(auditor.audit_file(target))
