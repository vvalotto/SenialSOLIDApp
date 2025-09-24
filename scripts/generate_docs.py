#!/usr/bin/env python3
"""
SSA-27: Automated API Documentation Generation Script

This script generates comprehensive API documentation using Sphinx with
automated docstring extraction and quality validation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Generate automated API documentation for SenialSOLIDApp.

    Implements SSA-27 documentation standards by generating comprehensive
    API documentation from Google Style docstrings and validating
    documentation quality against defined thresholds.

    Attributes:
        project_root: Path to the project root directory
        docs_dir: Path to the documentation directory
        sphinx_dir: Path to the Sphinx documentation directory
        build_dir: Path to the documentation build output
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize documentation generator.

        Args:
            project_root: Optional project root path. If None, auto-detected.
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.docs_dir = self.project_root / "docs"
        self.sphinx_dir = self.docs_dir / "sphinx"
        self.build_dir = self.sphinx_dir / "_build"

        # Quality thresholds from SSA-27
        self.quality_thresholds = {
            "docstring_coverage": 90.0,
            "build_success": True,
            "link_validation": True
        }

    def validate_environment(self) -> bool:
        """Validate that the documentation generation environment is ready.

        Returns:
            bool: True if environment is valid, False otherwise

        Raises:
            FileNotFoundError: When required directories don't exist
            ImportError: When required packages are not installed
        """
        logger.info("Validating documentation generation environment...")

        # Check required directories
        required_dirs = [self.project_root, self.docs_dir, self.sphinx_dir]
        for dir_path in required_dirs:
            if not dir_path.exists():
                logger.error(f"Required directory not found: {dir_path}")
                return False

        # Check required files
        conf_file = self.sphinx_dir / "conf.py"
        index_file = self.sphinx_dir / "index.rst"

        if not conf_file.exists():
            logger.error("Sphinx configuration file not found: conf.py")
            return False

        if not index_file.exists():
            logger.error("Sphinx index file not found: index.rst")
            return False

        # Check required Python packages
        required_packages = ["sphinx", "sphinx_rtd_theme", "pydocstyle"]
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                logger.error(f"Required package not installed: {package}")
                return False

        logger.info("Environment validation successful")
        return True

    def clean_build_directory(self) -> None:
        """Clean the documentation build directory.

        Removes all generated files to ensure a clean build.
        """
        logger.info("Cleaning documentation build directory...")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            logger.info(f"Removed build directory: {self.build_dir}")

        self.build_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Build directory cleaned and recreated")

    def run_pydocstyle_check(self) -> Dict[str, float]:
        """Run pydocstyle to validate docstring quality.

        Returns:
            Dict[str, float]: Docstring quality metrics

        Raises:
            subprocess.CalledProcessError: When pydocstyle execution fails
        """
        logger.info("Running pydocstyle documentation quality check...")

        try:
            # Run pydocstyle with coverage reporting
            cmd = [
                "pydocstyle",
                "--count",
                "--convention=google",
                str(self.project_root)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # Parse pydocstyle output for metrics
            metrics = self._parse_pydocstyle_output(result.stdout, result.stderr)

            logger.info(f"Docstring coverage: {metrics['coverage']:.1f}%")
            logger.info(f"Quality score: {metrics['quality_score']:.1f}/10.0")

            return metrics

        except FileNotFoundError:
            logger.error("pydocstyle not found. Install with: pip install pydocstyle")
            return {"coverage": 0.0, "quality_score": 0.0}

    def _parse_pydocstyle_output(self, stdout: str, stderr: str) -> Dict[str, float]:
        """Parse pydocstyle output to extract metrics.

        Args:
            stdout: Standard output from pydocstyle
            stderr: Standard error from pydocstyle

        Returns:
            Dict[str, float]: Parsed metrics
        """
        # Parse error count and calculate coverage/quality score
        error_lines = stderr.split('\n') if stderr else []
        error_count = len([line for line in error_lines if line.strip()])

        # Estimate coverage based on error count (simplified)
        # In production, this would use more sophisticated analysis
        total_functions = self._count_documentable_functions()
        if total_functions > 0:
            coverage = max(0, (total_functions - error_count) / total_functions * 100)
            quality_score = min(10.0, max(0, 10.0 - (error_count / total_functions * 5)))
        else:
            coverage = 100.0
            quality_score = 10.0

        return {
            "coverage": coverage,
            "quality_score": quality_score,
            "error_count": error_count
        }

    def _count_documentable_functions(self) -> int:
        """Count the total number of documentable functions in the project.

        Returns:
            int: Number of functions/classes that should have documentation
        """
        # Simplified count - in production, this would use AST analysis
        count = 0
        for py_file in self.project_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in ["test", "migration", "__pycache__"]):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    count += content.count("def ") + content.count("class ")
            except Exception as e:
                logger.warning(f"Could not analyze {py_file}: {e}")
        return count

    def generate_sphinx_docs(self) -> bool:
        """Generate documentation using Sphinx.

        Returns:
            bool: True if generation successful, False otherwise

        Raises:
            subprocess.CalledProcessError: When Sphinx build fails
        """
        logger.info("Generating Sphinx documentation...")

        try:
            # Run sphinx-build
            cmd = [
                "sphinx-build",
                "-W",  # Treat warnings as errors
                "-b", "html",  # HTML output
                str(self.sphinx_dir),  # Source directory
                str(self.build_dir / "html")  # Output directory
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0:
                logger.info("Sphinx documentation generated successfully")
                logger.info(f"Documentation available at: {self.build_dir / 'html' / 'index.html'}")
                return True
            else:
                logger.error("Sphinx build failed:")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False

        except FileNotFoundError:
            logger.error("sphinx-build not found. Install with: pip install sphinx")
            return False

    def validate_documentation_quality(self, metrics: Dict[str, float]) -> bool:
        """Validate generated documentation against quality thresholds.

        Args:
            metrics: Documentation quality metrics

        Returns:
            bool: True if quality thresholds are met, False otherwise
        """
        logger.info("Validating documentation quality against SSA-27 standards...")

        quality_passed = True

        # Check docstring coverage
        coverage = metrics.get("coverage", 0.0)
        threshold = self.quality_thresholds["docstring_coverage"]

        if coverage >= threshold:
            logger.info(f"✅ Docstring coverage: {coverage:.1f}% (>= {threshold}%)")
        else:
            logger.error(f"❌ Docstring coverage: {coverage:.1f}% (< {threshold}%)")
            quality_passed = False

        # Check build success
        build_success = (self.build_dir / "html" / "index.html").exists()
        if build_success:
            logger.info("✅ Documentation build: SUCCESS")
        else:
            logger.error("❌ Documentation build: FAILED")
            quality_passed = False

        return quality_passed

    def generate_documentation_report(self, metrics: Dict[str, float]) -> None:
        """Generate documentation quality report.

        Args:
            metrics: Documentation quality metrics
        """
        logger.info("Generating documentation quality report...")

        report_path = self.build_dir / "documentation_quality_report.md"

        report_content = f"""# Documentation Quality Report (SSA-27)

**Generated:** {self._get_timestamp()}
**Project:** SenialSOLIDApp
**Standards:** SSA-27 Google Style Documentation

## Quality Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Docstring Coverage | {metrics.get('coverage', 0):.1f}% | {self.quality_thresholds['docstring_coverage']}% | {'✅ PASS' if metrics.get('coverage', 0) >= self.quality_thresholds['docstring_coverage'] else '❌ FAIL'} |
| Quality Score | {metrics.get('quality_score', 0):.1f}/10.0 | 9.0/10.0 | {'✅ PASS' if metrics.get('quality_score', 0) >= 9.0 else '❌ FAIL'} |
| Build Success | {'✅ SUCCESS' if (self.build_dir / "html" / "index.html").exists() else '❌ FAILED'} | Required | {'✅ PASS' if (self.build_dir / "html" / "index.html").exists() else '❌ FAIL'} |

## Documentation Output

- **HTML Documentation:** `{self.build_dir / 'html' / 'index.html'}`
- **API Reference:** Complete auto-generated API documentation
- **Quality Standards:** Google Style docstrings (PEP 257)

## Next Steps

{"Documentation meets SSA-27 quality standards. No action required." if self.validate_documentation_quality(metrics) else "Documentation quality below thresholds. Review and improve docstrings."}

---
*Report generated by SSA-27 Documentation Generator*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"Documentation quality report saved: {report_path}")

    def _get_timestamp(self) -> str:
        """Get current timestamp for reporting.

        Returns:
            str: Formatted timestamp
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_full_generation(self, clean: bool = True) -> bool:
        """Run the complete documentation generation process.

        Args:
            clean: Whether to clean build directory before generation

        Returns:
            bool: True if generation successful and quality thresholds met
        """
        logger.info("Starting SSA-27 documentation generation process...")

        # Validate environment
        if not self.validate_environment():
            logger.error("Environment validation failed")
            return False

        # Clean build directory if requested
        if clean:
            self.clean_build_directory()

        # Run documentation quality checks
        metrics = self.run_pydocstyle_check()

        # Generate Sphinx documentation
        build_success = self.generate_sphinx_docs()
        metrics["build_success"] = build_success

        # Validate quality
        quality_passed = self.validate_documentation_quality(metrics)

        # Generate report
        self.generate_documentation_report(metrics)

        if quality_passed and build_success:
            logger.info("🎉 Documentation generation completed successfully!")
            logger.info(f"📖 View documentation: {self.build_dir / 'html' / 'index.html'}")
            return True
        else:
            logger.error("❌ Documentation generation failed quality checks")
            return False


def main():
    """Main entry point for documentation generation script."""
    parser = argparse.ArgumentParser(
        description="Generate automated API documentation (SSA-27)"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't clean build directory before generation"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory (auto-detected if not specified)"
    )

    args = parser.parse_args()

    try:
        generator = DocumentationGenerator(args.project_root)
        success = generator.run_full_generation(clean=not args.no_clean)
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("Documentation generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()