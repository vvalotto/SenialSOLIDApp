"""
Validation Pipeline for SSA-24 Input Validation Framework

Orchestrates multiple validators and manages validation workflow
"""

from typing import List, Dict, Any, Optional, Union, Callable
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .validator_base import AbstractValidator, ValidationResult
from ..exceptions.validation_exceptions import ValidationPipelineError, ValidationError


class PipelineMode(Enum):
    """Execution modes for validation pipeline"""
    FAIL_FAST = "fail_fast"          # Stop on first error
    COLLECT_ALL = "collect_all"      # Collect all errors before failing
    WARN_ONLY = "warn_only"          # Convert errors to warnings


class PipelineStage(Enum):
    """Stages in the validation pipeline"""
    PRE_VALIDATION = "pre_validation"
    TYPE_VALIDATION = "type_validation"
    BUSINESS_VALIDATION = "business_validation"
    SECURITY_VALIDATION = "security_validation"
    POST_VALIDATION = "post_validation"


class ValidationPipeline:
    """
    Orchestrates multiple validators in a structured pipeline

    Supports different execution modes, parallel execution, and detailed reporting
    """

    def __init__(
        self,
        name: str,
        mode: PipelineMode = PipelineMode.COLLECT_ALL,
        parallel_execution: bool = False,
        max_workers: int = 4,
        timeout: float = 30.0
    ):
        self.name = name
        self.mode = mode
        self.parallel_execution = parallel_execution
        self.max_workers = max_workers
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.ValidationPipeline")

        # Pipeline stages with validators
        self.stages: Dict[PipelineStage, List[AbstractValidator]] = {
            stage: [] for stage in PipelineStage
        }

        # Pipeline hooks
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []

        # Pipeline statistics
        self.stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_execution_time': 0.0
        }

    def add_validator(
        self,
        validator: AbstractValidator,
        stage: PipelineStage = PipelineStage.BUSINESS_VALIDATION
    ):
        """Add a validator to a specific pipeline stage"""
        if not validator.is_enabled():
            self.logger.warning(f"Adding disabled validator {validator.name} to pipeline")

        self.stages[stage].append(validator)
        self.logger.info(f"Added validator {validator.name} to stage {stage.value}")

    def remove_validator(self, validator_name: str, stage: PipelineStage = None) -> bool:
        """Remove a validator by name from specified stage or all stages"""
        removed = False

        if stage:
            stages_to_check = [stage]
        else:
            stages_to_check = list(PipelineStage)

        for stage_key in stages_to_check:
            initial_count = len(self.stages[stage_key])
            self.stages[stage_key] = [
                v for v in self.stages[stage_key]
                if v.name != validator_name
            ]
            if len(self.stages[stage_key]) < initial_count:
                removed = True
                self.logger.info(f"Removed validator {validator_name} from stage {stage_key.value}")

        return removed

    def add_pre_hook(self, hook: Callable):
        """Add a pre-validation hook"""
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable):
        """Add a post-validation hook"""
        self.post_hooks.append(hook)

    def add_error_hook(self, hook: Callable):
        """Add an error handling hook"""
        self.error_hooks.append(hook)

    def validate(
        self,
        value: Any,
        context: Dict[str, Any] = None,
        stages_to_run: List[PipelineStage] = None
    ) -> ValidationResult:
        """
        Execute the validation pipeline

        Args:
            value: Value to validate
            context: Optional context for validation
            stages_to_run: Specific stages to run (default: all)

        Returns:
            Combined ValidationResult from all validators
        """
        start_time = time.time()
        context = context or {}
        stages_to_run = stages_to_run or list(PipelineStage)

        # Initialize result
        pipeline_result = ValidationResult(is_valid=True, sanitized_value=value)
        pipeline_result.metadata['pipeline_name'] = self.name
        pipeline_result.metadata['execution_mode'] = self.mode.value
        pipeline_result.metadata['stages_executed'] = []

        try:
            # Execute pre-hooks
            self._execute_hooks(self.pre_hooks, value, context)

            # Execute pipeline stages
            for stage in stages_to_run:
                if stage not in self.stages:
                    continue

                stage_validators = [v for v in self.stages[stage] if v.is_enabled()]
                if not stage_validators:
                    continue

                self.logger.debug(f"Executing stage {stage.value} with {len(stage_validators)} validators")

                stage_result = self._execute_stage(stage, stage_validators, value, context)
                pipeline_result.metadata['stages_executed'].append(stage.value)

                # Merge stage results
                self._merge_results(pipeline_result, stage_result)

                # Update value for next stage if sanitized
                if stage_result.sanitized_value is not None:
                    value = stage_result.sanitized_value
                    pipeline_result.sanitized_value = value

                # Handle fail-fast mode
                if self.mode == PipelineMode.FAIL_FAST and stage_result.has_errors():
                    pipeline_result.is_valid = False
                    break

            # Handle warn-only mode
            if self.mode == PipelineMode.WARN_ONLY and pipeline_result.has_errors():
                # Convert errors to warnings
                for error in pipeline_result.errors:
                    pipeline_result.add_warning(f"Validation warning: {error.message}")
                pipeline_result.errors = []
                pipeline_result.is_valid = True

            # Execute post-hooks
            self._execute_hooks(self.post_hooks, value, context, pipeline_result)

        except Exception as e:
            # Execute error hooks
            self._execute_hooks(self.error_hooks, value, context, e)

            error = ValidationPipelineError(
                message=f"Pipeline execution failed: {str(e)}",
                pipeline_stage=getattr(e, 'stage', 'unknown'),
                cause=e
            )
            pipeline_result.add_error(error)

        finally:
            # Update statistics
            execution_time = time.time() - start_time
            self._update_stats(pipeline_result.is_valid, execution_time)

            pipeline_result.metadata['execution_time'] = execution_time
            pipeline_result.metadata['total_validators'] = sum(
                len(validators) for validators in self.stages.values()
            )

        return pipeline_result

    def _execute_stage(
        self,
        stage: PipelineStage,
        validators: List[AbstractValidator],
        value: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Execute validators in a specific stage"""
        stage_result = ValidationResult(is_valid=True, sanitized_value=value)

        if self.parallel_execution and len(validators) > 1:
            # Parallel execution
            stage_result = self._execute_parallel(validators, value, context)
        else:
            # Sequential execution
            stage_result = self._execute_sequential(validators, value, context)

        return stage_result

    def _execute_sequential(
        self,
        validators: List[AbstractValidator],
        value: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Execute validators sequentially"""
        combined_result = ValidationResult(is_valid=True, sanitized_value=value)

        for validator in validators:
            try:
                result = validator.validate(value, context)
                self._merge_results(combined_result, result)

                # Update value if sanitized
                if result.sanitized_value is not None:
                    value = result.sanitized_value
                    combined_result.sanitized_value = value

                # Fail fast check
                if self.mode == PipelineMode.FAIL_FAST and result.has_errors():
                    break

            except Exception as e:
                error = ValidationPipelineError(
                    message=f"Validator {validator.name} failed: {str(e)}",
                    pipeline_stage=validator.name,
                    failed_validators=[validator.name],
                    cause=e
                )
                combined_result.add_error(error)

                if self.mode == PipelineMode.FAIL_FAST:
                    break

        return combined_result

    def _execute_parallel(
        self,
        validators: List[AbstractValidator],
        value: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Execute validators in parallel"""
        combined_result = ValidationResult(is_valid=True, sanitized_value=value)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all validation tasks
            future_to_validator = {
                executor.submit(validator.validate, value, context): validator
                for validator in validators
            }

            # Collect results
            for future in as_completed(future_to_validator, timeout=self.timeout):
                validator = future_to_validator[future]
                try:
                    result = future.result()
                    self._merge_results(combined_result, result)

                    # Note: Parallel execution doesn't support value chaining
                    # Each validator works on the original value

                except Exception as e:
                    error = ValidationPipelineError(
                        message=f"Validator {validator.name} failed: {str(e)}",
                        pipeline_stage=validator.name,
                        failed_validators=[validator.name],
                        cause=e
                    )
                    combined_result.add_error(error)

        return combined_result

    def _merge_results(self, target: ValidationResult, source: ValidationResult):
        """Merge source validation result into target"""
        if source.has_errors():
            target.is_valid = False
            target.errors.extend(source.errors)

        target.warnings.extend(source.warnings)
        target.metadata.update(source.metadata)

    def _execute_hooks(self, hooks: List[Callable], *args, **kwargs):
        """Execute a list of hooks safely"""
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Hook execution failed: {str(e)}")

    def _update_stats(self, is_valid: bool, execution_time: float):
        """Update pipeline execution statistics"""
        self.stats['total_validations'] += 1

        if is_valid:
            self.stats['successful_validations'] += 1
        else:
            self.stats['failed_validations'] += 1

        # Update average execution time
        total = self.stats['total_validations']
        current_avg = self.stats['average_execution_time']
        self.stats['average_execution_time'] = (
            (current_avg * (total - 1) + execution_time) / total
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        return self.stats.copy()

    def get_validator_count(self) -> Dict[str, int]:
        """Get count of validators by stage"""
        return {
            stage.value: len(validators)
            for stage, validators in self.stages.items()
        }

    def is_empty(self) -> bool:
        """Check if pipeline has any validators"""
        return all(len(validators) == 0 for validators in self.stages.values())

    def clear(self):
        """Remove all validators from all stages"""
        for stage in self.stages:
            self.stages[stage].clear()
        self.logger.info(f"Cleared all validators from pipeline {self.name}")

    def __str__(self) -> str:
        validator_count = sum(len(validators) for validators in self.stages.values())
        return f"ValidationPipeline(name='{self.name}', validators={validator_count}, mode={self.mode.value})"

    def __repr__(self) -> str:
        return (
            f"ValidationPipeline("
            f"name='{self.name}', "
            f"mode={self.mode.value}, "
            f"parallel={self.parallel_execution}, "
            f"stages={self.get_validator_count()})"
        )