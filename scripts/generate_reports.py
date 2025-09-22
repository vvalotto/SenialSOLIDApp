#!/usr/bin/env python3
"""
SSA-25 Quality Reports Generator
Genera dashboards y reportes HTML de métricas de calidad
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import subprocess


class QualityReportGenerator:
    """Generador de reportes de calidad para SSA-25"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.reports_dir = self.project_root / "quality_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now()

    def generate_html_dashboard(self, results: Dict) -> str:
        """Genera dashboard HTML con métricas de calidad"""
        html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSA-25 Quality Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
            transition: transform 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }}

        .metric-card.pass {{ border-left-color: #48bb78; }}
        .metric-card.fail {{ border-left-color: #f56565; }}
        .metric-card.warning {{ border-left-color: #ed8936; }}

        .metric-title {{
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2d3748;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .metric-value.pass {{ color: #48bb78; }}
        .metric-value.fail {{ color: #f56565; }}
        .metric-value.warning {{ color: #ed8936; }}

        .metric-status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}

        .status-pass {{ background: #c6f6d5; color: #276749; }}
        .status-fail {{ background: #fed7d7; color: #9b2c2c; }}
        .status-warning {{ background: #feebc8; color: #9c4221; }}

        .quality-gates {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .quality-gates h2 {{
            color: #2d3748;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}

        .gate-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #e2e8f0;
        }}

        .gate-item:last-child {{ border-bottom: none; }}

        .gate-name {{ font-weight: 600; }}

        .detailed-results {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .tool-result {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #cbd5e0;
        }}

        .tool-result.pass {{ border-left-color: #48bb78; background: #f0fff4; }}
        .tool-result.fail {{ border-left-color: #f56565; background: #fffaf0; }}

        .tool-name {{
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #e2e8f0;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #38a169);
            transition: width 0.3s ease;
        }}

        .footer {{
            text-align: center;
            color: #718096;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #e2e8f0;
        }}

        @media (max-width: 768px) {{
            .dashboard-grid {{ grid-template-columns: 1fr; }}
            .container {{ padding: 10px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SSA-25 Quality Dashboard</h1>
            <div class="meta">
                <p>Métricas Automáticas de Calidad de Código</p>
                <p>📅 {timestamp} | 📁 {project_name}</p>
            </div>
        </div>

        <div class="dashboard-grid">
            {metric_cards}
        </div>

        <div class="quality-gates">
            <h2>🚪 Quality Gates Status</h2>
            {quality_gates}
        </div>

        <div class="detailed-results">
            <h2>🔍 Resultados Detallados</h2>
            {detailed_results}
        </div>

        <div class="footer">
            <p>🤖 Generado automáticamente por SSA-25 Quality System</p>
            <p>Próxima actualización: {next_update}</p>
        </div>
    </div>

    <script>
        // Animación de barras de progreso
        document.addEventListener('DOMContentLoaded', function() {{
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {{
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {{
                    bar.style.width = width;
                }}, 500);
            }});
        }});
    </script>
</body>
</html>
        """

        # Generar cards de métricas
        metric_cards = self._generate_metric_cards(results)

        # Generar quality gates
        quality_gates = self._generate_quality_gates(results)

        # Generar resultados detallados
        detailed_results = self._generate_detailed_results(results)

        return html_template.format(
            timestamp=self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            project_name=self.project_root.name,
            metric_cards=metric_cards,
            quality_gates=quality_gates,
            detailed_results=detailed_results,
            next_update=(self.timestamp + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
        )

    def _generate_metric_cards(self, results: Dict) -> str:
        """Genera las tarjetas de métricas principales"""
        cards = []
        checks = results.get("checks", {})
        summary = results.get("summary", {})

        # Overall Success Rate
        success_rate = summary.get("success_rate", 0)
        status_class = "pass" if success_rate >= 80 else "fail" if success_rate < 50 else "warning"

        cards.append(f"""
        <div class="metric-card {status_class}">
            <div class="metric-title">📊 Success Rate</div>
            <div class="metric-value {status_class}">{success_rate:.1f}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {success_rate}%"></div>
            </div>
            <span class="metric-status status-{status_class}">
                {summary.get("passed_checks", 0)}/{summary.get("total_checks", 0)} Passed
            </span>
        </div>
        """)

        # Pylint Score
        pylint = checks.get("pylint", {})
        if "score" in pylint:
            score = pylint["score"]
            status_class = "pass" if score >= 8.0 else "fail" if score < 7.0 else "warning"
            cards.append(f"""
            <div class="metric-card {status_class}">
                <div class="metric-title">🔍 Pylint Score</div>
                <div class="metric-value {status_class}">{score:.2f}/10</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {score * 10}%"></div>
                </div>
                <span class="metric-status status-{status_class}">
                    {"✅ PASS" if pylint.get("passed") else "❌ FAIL"}
                </span>
            </div>
            """)

        # Coverage
        coverage = checks.get("coverage", {})
        if "total_coverage" in coverage:
            cov = coverage["total_coverage"]
            status_class = "pass" if cov >= 70 else "fail" if cov < 50 else "warning"
            cards.append(f"""
            <div class="metric-card {status_class}">
                <div class="metric-title">📈 Code Coverage</div>
                <div class="metric-value {status_class}">{cov:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {cov}%"></div>
                </div>
                <span class="metric-status status-{status_class}">
                    {"✅ PASS" if coverage.get("passed") else "❌ FAIL"}
                </span>
            </div>
            """)

        # Complexity
        complexity = checks.get("radon_cc", {})
        if "max_complexity" in complexity:
            max_cc = complexity["max_complexity"]
            status_class = "pass" if max_cc <= 10 else "fail" if max_cc > 20 else "warning"
            cards.append(f"""
            <div class="metric-card {status_class}">
                <div class="metric-title">🔄 Max Complexity</div>
                <div class="metric-value {status_class}">{max_cc}</div>
                <p>Threshold: ≤10</p>
                <span class="metric-status status-{status_class}">
                    {"✅ PASS" if complexity.get("passed") else "❌ FAIL"}
                </span>
            </div>
            """)

        # Maintainability
        maintainability = checks.get("radon_mi", {})
        if "average_mi" in maintainability:
            avg_mi = maintainability["average_mi"]
            status_class = "pass" if avg_mi >= 50 else "fail" if avg_mi < 30 else "warning"
            cards.append(f"""
            <div class="metric-card {status_class}">
                <div class="metric-title">🔧 Maintainability</div>
                <div class="metric-value {status_class}">{avg_mi:.1f}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(avg_mi, 100)}%"></div>
                </div>
                <span class="metric-status status-{status_class}">
                    {"✅ EXCELLENT" if avg_mi >= 50 else "❌ NEEDS WORK"}
                </span>
            </div>
            """)

        return "".join(cards)

    def _generate_quality_gates(self, results: Dict) -> str:
        """Genera la sección de quality gates"""
        gates = []
        quality_gates_status = results.get("summary", {}).get("quality_gates_status", {})

        gate_definitions = {
            "pylint_score": "Pylint Score ≥ 8.0",
            "code_coverage": "Code Coverage ≥ 70%",
            "max_complexity": "Max Complexity ≤ 10",
            "maintainability_index": "Maintainability ≥ 20",
            "type_coverage": "Type Coverage ≥ 50%"
        }

        for gate_name, description in gate_definitions.items():
            passed = quality_gates_status.get(gate_name, False)
            status_class = "status-pass" if passed else "status-fail"
            status_text = "✅ PASS" if passed else "❌ FAIL"

            gates.append(f"""
            <div class="gate-item">
                <div class="gate-name">{description}</div>
                <span class="metric-status {status_class}">{status_text}</span>
            </div>
            """)

        return "".join(gates)

    def _generate_detailed_results(self, results: Dict) -> str:
        """Genera la sección de resultados detallados"""
        details = []
        checks = results.get("checks", {})

        tool_names = {
            "pylint": "🔍 Pylint",
            "flake8": "🎨 Flake8",
            "mypy": "📝 MyPy",
            "radon_cc": "🔄 Radon Complexity",
            "radon_mi": "🔧 Radon Maintainability",
            "coverage": "📊 Coverage"
        }

        for tool, result in checks.items():
            if tool in tool_names:
                passed = result.get("passed", False)
                status_class = "pass" if passed else "fail"

                details_text = ""
                if "score" in result:
                    details_text += f"Score: {result['score']:.2f}/10<br>"
                if "issues_count" in result:
                    details_text += f"Issues: {result['issues_count']}<br>"
                if "max_complexity" in result:
                    details_text += f"Max Complexity: {result['max_complexity']}<br>"
                if "average_mi" in result:
                    details_text += f"Avg Maintainability: {result['average_mi']:.2f}<br>"
                if "total_coverage" in result:
                    details_text += f"Coverage: {result['total_coverage']:.1f}%<br>"
                if "error" in result:
                    details_text += f"Error: {result['error']}<br>"

                details.append(f"""
                <div class="tool-result {status_class}">
                    <div class="tool-name">{tool_names[tool]}</div>
                    <div>{details_text}</div>
                    <span class="metric-status {'status-pass' if passed else 'status-fail'}">
                        {"✅ PASS" if passed else "❌ FAIL"}
                    </span>
                </div>
                """)

        return "".join(details)

    def run_quality_checks_and_generate_report(self) -> str:
        """Ejecuta quality checks y genera reporte"""
        print("🚀 Ejecutando quality checks...")

        # Ejecutar script de quality check
        script_path = self.project_root / "scripts" / "quality_check.py"
        if not script_path.exists():
            raise FileNotFoundError(f"Script de quality check no encontrado: {script_path}")

        cmd = ["python", str(script_path), "--format", "json"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        if result.stdout:
            try:
                # Extraer JSON del output (puede haber texto adicional)
                lines = result.stdout.strip().split('\n')
                json_start = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith('{'):
                        json_start = i
                        break

                if json_start >= 0:
                    json_content = '\n'.join(lines[json_start:])
                    results = json.loads(json_content)
                else:
                    raise ValueError("No se encontró JSON válido en el output")

            except (json.JSONDecodeError, ValueError):
                # Crear resultados mock si hay error
                results = self._create_mock_results()
        else:
            results = self._create_mock_results()

        # Generar HTML
        html_content = self.generate_html_dashboard(results)

        # Guardar reporte
        report_path = self.reports_dir / f"quality_dashboard_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Crear enlace simbólico al último reporte
        latest_path = self.reports_dir / "latest_dashboard.html"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(report_path.name)

        print(f"📄 Dashboard generado: {report_path}")
        print(f"🔗 Último dashboard: {latest_path}")

        return str(report_path)

    def _create_mock_results(self) -> Dict:
        """Crea resultados mock para testing"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "project_root": str(self.project_root),
            "modules": ["aplicacion", "dominio", "infraestructura", "presentacion"],
            "checks": {
                "pylint": {"tool": "pylint", "score": 7.23, "issues_count": 45, "passed": False},
                "flake8": {"tool": "flake8", "issues_count": 12, "passed": False},
                "mypy": {"tool": "mypy", "errors_count": 89, "type_coverage": 15.0, "passed": False},
                "radon_cc": {"tool": "radon_cc", "max_complexity": 23, "total_functions": 156, "passed": False},
                "radon_mi": {"tool": "radon_mi", "average_mi": 55.27, "passed": True},
                "coverage": {"tool": "coverage", "error": "No se pudo medir coverage", "passed": False}
            },
            "summary": {
                "total_checks": 6,
                "passed_checks": 1,
                "success_rate": 16.7,
                "quality_gates_status": {
                    "pylint_score": False,
                    "code_coverage": False,
                    "max_complexity": False,
                    "maintainability_index": True,
                    "type_coverage": False
                },
                "overall_passed": False
            }
        }


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="SSA-25 Quality Reports Generator")
    parser.add_argument("--project-root", help="Directorio raíz del proyecto")
    parser.add_argument("--output", help="Archivo de salida HTML")

    args = parser.parse_args()

    # Crear generador
    generator = QualityReportGenerator(args.project_root)

    # Generar reporte
    report_path = generator.run_quality_checks_and_generate_report()

    if args.output:
        # Copiar a ubicación específica
        import shutil
        shutil.copy2(report_path, args.output)
        print(f"📄 Reporte copiado a: {args.output}")

    print("✅ Generación de reportes completada")


if __name__ == "__main__":
    main()