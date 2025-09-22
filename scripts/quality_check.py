#!/usr/bin/env python3
"""
SSA-25 Quality Check Script
Ejecuta todas las herramientas de calidad de código de forma automatizada
"""

import os
import sys
import subprocess
import argparse
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile


class QualityChecker:
    """Ejecutor automático de quality checks para SSA-25"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = {}
        self.quality_gates = self._load_quality_gates()
        self.timestamp = datetime.now().isoformat()

    def _load_quality_gates(self) -> Dict:
        """Carga la configuración de quality gates"""
        gates_file = self.project_root / "quality_gates.yaml"
        if gates_file.exists():
            with open(gates_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def run_pylint(self, modules: List[str]) -> Dict:
        """Ejecuta pylint y devuelve el score"""
        print("🔍 Ejecutando Pylint...")

        cmd = ["pylint"] + modules + ["--output-format=json", "--score=y"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # Extraer score de stderr (pylint envía score ahí)
            score_line = [line for line in result.stderr.split('\n')
                         if 'Your code has been rated' in line]

            score = 0.0
            if score_line:
                score_text = score_line[0].split('at ')[1].split('/')[0]
                score = float(score_text)

            # Parsear issues JSON
            issues = []
            if result.stdout.strip():
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    issues = []

            return {
                "tool": "pylint",
                "score": score,
                "issues_count": len(issues),
                "issues": issues,
                "passed": score >= self.quality_gates.get('quality_gates', {}).get('pylint_score', {}).get('threshold', 8.0)
            }

        except Exception as e:
            return {
                "tool": "pylint",
                "error": str(e),
                "passed": False
            }

    def run_flake8(self, modules: List[str]) -> Dict:
        """Ejecuta flake8 para style checking"""
        print("🎨 Ejecutando Flake8...")

        cmd = ["flake8"] + modules + ["--format=json"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            issues = []
            if result.stdout.strip():
                try:
                    # Flake8 con formato JSON puede no estar disponible
                    # Parseamos formato estándar
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            parts = line.split(':')
                            if len(parts) >= 4:
                                issues.append({
                                    "file": parts[0],
                                    "line": parts[1],
                                    "column": parts[2],
                                    "code": parts[3].split()[0],
                                    "message": ':'.join(parts[3:])
                                })
                except:
                    issues = []

            return {
                "tool": "flake8",
                "issues_count": len(issues),
                "issues": issues,
                "passed": len(issues) == 0
            }

        except Exception as e:
            return {
                "tool": "flake8",
                "error": str(e),
                "passed": False
            }

    def run_mypy(self, modules: List[str]) -> Dict:
        """Ejecuta mypy para type checking"""
        print("📝 Ejecutando MyPy...")

        cmd = ["mypy"] + modules + ["--no-error-summary"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # Contar errores
            error_lines = [line for line in result.stdout.split('\n')
                          if ': error:' in line]

            type_coverage = self._estimate_type_coverage(result.stdout)

            return {
                "tool": "mypy",
                "errors_count": len(error_lines),
                "type_coverage": type_coverage,
                "passed": type_coverage >= self.quality_gates.get('quality_gates', {}).get('type_coverage', {}).get('threshold', 50.0)
            }

        except Exception as e:
            return {
                "tool": "mypy",
                "error": str(e),
                "passed": False
            }

    def _estimate_type_coverage(self, mypy_output: str) -> float:
        """Estima la cobertura de tipos basada en errores de mypy"""
        # Estimación simple: menos errores = mejor cobertura
        total_lines = mypy_output.count('\n')
        error_lines = mypy_output.count(': error:')

        if total_lines == 0:
            return 0.0

        # Estimación básica: 100% - (errores/líneas totales * 100)
        coverage = max(0, 100 - (error_lines / max(total_lines, 1) * 100))
        return min(coverage, 100.0)

    def run_radon_complexity(self, modules: List[str]) -> Dict:
        """Ejecuta radon para análisis de complejidad"""
        print("🔄 Ejecutando Radon (Complexity)...")

        cmd = ["radon", "cc"] + modules + ["-s", "-j"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            complexity_data = {}
            if result.stdout.strip():
                try:
                    complexity_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    complexity_data = {}

            # Encontrar complejidad máxima
            max_complexity = 0
            total_functions = 0

            for file_data in complexity_data.values():
                for item in file_data:
                    if 'complexity' in item:
                        complexity = item['complexity']
                        max_complexity = max(max_complexity, complexity)
                        total_functions += 1

            threshold = self.quality_gates.get('quality_gates', {}).get('max_complexity', {}).get('threshold', 10)

            return {
                "tool": "radon_cc",
                "max_complexity": max_complexity,
                "total_functions": total_functions,
                "data": complexity_data,
                "passed": max_complexity <= threshold
            }

        except Exception as e:
            return {
                "tool": "radon_cc",
                "error": str(e),
                "passed": False
            }

    def run_radon_maintainability(self, modules: List[str]) -> Dict:
        """Ejecuta radon para índice de mantenibilidad"""
        print("🔧 Ejecutando Radon (Maintainability)...")

        cmd = ["radon", "mi"] + modules + ["-s", "-j"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            mi_data = {}
            if result.stdout.strip():
                try:
                    mi_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    mi_data = {}

            # Calcular promedio de mantenibilidad
            mi_scores = []
            for file_data in mi_data.values():
                if isinstance(file_data, dict) and 'mi' in file_data:
                    mi_scores.append(file_data['mi'])

            avg_mi = sum(mi_scores) / len(mi_scores) if mi_scores else 0

            threshold = self.quality_gates.get('quality_gates', {}).get('maintainability_index', {}).get('threshold', 20.0)

            return {
                "tool": "radon_mi",
                "average_mi": avg_mi,
                "scores": mi_scores,
                "data": mi_data,
                "passed": avg_mi >= threshold
            }

        except Exception as e:
            return {
                "tool": "radon_mi",
                "error": str(e),
                "passed": False
            }

    def run_coverage(self) -> Dict:
        """Ejecuta coverage.py para medir cobertura de código"""
        print("📊 Ejecutando Coverage...")

        try:
            # Ejecutar tests con coverage
            cmd_run = ["coverage", "run", "-m", "pytest", "tests/"]
            subprocess.run(cmd_run, cwd=self.project_root, capture_output=True)

            # Obtener reporte
            cmd_report = ["coverage", "report", "--format=json"]
            result = subprocess.run(
                cmd_report,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.stdout.strip():
                try:
                    coverage_data = json.loads(result.stdout)
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)

                    threshold = self.quality_gates.get('quality_gates', {}).get('code_coverage', {}).get('threshold', 70.0)

                    return {
                        "tool": "coverage",
                        "total_coverage": total_coverage,
                        "data": coverage_data,
                        "passed": total_coverage >= threshold
                    }
                except json.JSONDecodeError:
                    pass

            return {
                "tool": "coverage",
                "error": "No se pudo obtener datos de coverage",
                "passed": False
            }

        except Exception as e:
            return {
                "tool": "coverage",
                "error": str(e),
                "passed": False
            }

    def run_all_checks(self, modules: List[str] = None) -> Dict:
        """Ejecuta todos los quality checks"""
        if modules is None:
            modules = ["aplicacion", "dominio", "infraestructura", "presentacion", "config"]

        print(f"🚀 Ejecutando Quality Checks para SSA-25")
        print(f"📁 Proyecto: {self.project_root}")
        print(f"📦 Módulos: {', '.join(modules)}")
        print("=" * 60)

        self.results = {
            "timestamp": self.timestamp,
            "project_root": str(self.project_root),
            "modules": modules,
            "checks": {}
        }

        # Ejecutar cada herramienta
        self.results["checks"]["pylint"] = self.run_pylint(modules)
        self.results["checks"]["flake8"] = self.run_flake8(modules)
        self.results["checks"]["mypy"] = self.run_mypy(modules)
        self.results["checks"]["radon_cc"] = self.run_radon_complexity(modules)
        self.results["checks"]["radon_mi"] = self.run_radon_maintainability(modules)
        self.results["checks"]["coverage"] = self.run_coverage()

        # Calcular summary
        self.results["summary"] = self._calculate_summary()

        return self.results

    def _calculate_summary(self) -> Dict:
        """Calcula resumen de resultados"""
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for check in self.results["checks"].values() if check.get("passed", False))

        # Quality Gates Status
        gates_status = {}
        for gate_name, gate_config in self.quality_gates.get('quality_gates', {}).items():
            tool_name = gate_config.get('metric', gate_name)
            if tool_name in self.results["checks"]:
                gates_status[gate_name] = self.results["checks"][tool_name].get("passed", False)

        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            "quality_gates_status": gates_status,
            "overall_passed": passed_checks == total_checks
        }

    def generate_report(self, format_type: str = "console") -> str:
        """Genera reporte en formato especificado"""
        if format_type == "json":
            return json.dumps(self.results, indent=2)
        elif format_type == "yaml":
            return yaml.dump(self.results, default_flow_style=False)
        else:  # console
            return self._generate_console_report()

    def _generate_console_report(self) -> str:
        """Genera reporte para consola"""
        lines = []
        lines.append("=" * 60)
        lines.append("🎯 SSA-25 QUALITY CHECK REPORT")
        lines.append("=" * 60)
        lines.append(f"⏰ Timestamp: {self.timestamp}")
        lines.append(f"📁 Project: {self.project_root}")
        lines.append("")

        # Summary
        summary = self.results.get("summary", {})
        lines.append("📊 SUMMARY:")
        lines.append(f"  Total Checks: {summary.get('total_checks', 0)}")
        lines.append(f"  Passed: {summary.get('passed_checks', 0)}")
        lines.append(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
        lines.append(f"  Overall: {'✅ PASS' if summary.get('overall_passed') else '❌ FAIL'}")
        lines.append("")

        # Individual results
        lines.append("🔍 DETAILED RESULTS:")
        for tool, result in self.results.get("checks", {}).items():
            status = "✅ PASS" if result.get("passed") else "❌ FAIL"
            lines.append(f"  {tool.upper():15} {status}")

            if "score" in result:
                lines.append(f"                  Score: {result['score']:.2f}")
            if "issues_count" in result:
                lines.append(f"                  Issues: {result['issues_count']}")
            if "max_complexity" in result:
                lines.append(f"                  Max Complexity: {result['max_complexity']}")
            if "average_mi" in result:
                lines.append(f"                  Avg Maintainability: {result['average_mi']:.2f}")
            if "total_coverage" in result:
                lines.append(f"                  Coverage: {result['total_coverage']:.1f}%")
            if "error" in result:
                lines.append(f"                  Error: {result['error']}")

        lines.append("")
        lines.append("🚪 QUALITY GATES STATUS:")
        for gate, passed in summary.get('quality_gates_status', {}).items():
            status = "✅ PASS" if passed else "❌ FAIL"
            lines.append(f"  {gate:20} {status}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def save_report(self, filepath: str, format_type: str = "json"):
        """Guarda el reporte en archivo"""
        report_content = self.generate_report(format_type)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📄 Reporte guardado en: {filepath}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="SSA-25 Quality Check Script")
    parser.add_argument("--modules", nargs="+",
                       default=["aplicacion", "dominio", "infraestructura", "presentacion", "config"],
                       help="Módulos a analizar")
    parser.add_argument("--format", choices=["console", "json", "yaml"],
                       default="console", help="Formato de salida")
    parser.add_argument("--output", help="Archivo de salida (opcional)")
    parser.add_argument("--project-root", help="Directorio raíz del proyecto")

    args = parser.parse_args()

    # Crear checker
    checker = QualityChecker(args.project_root)

    # Ejecutar checks
    results = checker.run_all_checks(args.modules)

    # Mostrar reporte
    report = checker.generate_report(args.format)
    print(report)

    # Guardar si se especifica archivo
    if args.output:
        checker.save_report(args.output, args.format)

    # Exit code basado en resultados
    overall_passed = results.get("summary", {}).get("overall_passed", False)
    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()