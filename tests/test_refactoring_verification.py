"""
Test suite to verify refactoring changes from commit b8b7137.

Tests verify:
1. scan_project_directory consolidation (Priority 3)
2. Error handling improvements (Priority 2)
3. Legacy code removal (Priority 8)
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from project_planner.utils import scan_project_directory, count_building_blocks, count_sprints
from project_planner.api import _find_most_recent_output
from project_planner import models


# ============================================================================
# Test 1: scan_project_directory Consolidation (Priority 3)
# ============================================================================

class TestScanProjectDirectoryConsolidation:
    """Verify scan_project_directory was successfully consolidated."""

    def test_import_from_utils(self):
        """Verify api.py imports scan_project_directory from utils."""
        from project_planner import api

        # Should not have its own scan_project_directory function
        assert not hasattr(api, 'scan_project_directory') or \
               api.scan_project_directory.__module__ == 'project_planner.utils', \
               "api.py should import scan_project_directory from utils, not define its own"

    def test_scan_project_directory_exists(self):
        """Verify scan_project_directory function exists in utils."""
        assert callable(scan_project_directory), \
               "scan_project_directory should be a callable function"

    def test_scan_empty_directory(self):
        """Test scanning an empty project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = scan_project_directory(Path(tmpdir))

            # Should return dict with expected structure
            assert isinstance(result, dict)
            assert 'project_spec' in result
            assert 'diagrams' in result
            assert 'components' in result
            assert 'component_breakdown' in result  # Added for api.py compatibility

            # All should be None or empty
            assert result['project_spec'] is None
            assert result['diagrams'] == []
            assert result['components'] == []

    def test_scan_with_components(self):
        """Test scanning directory with components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create components directory with subdirectories
            components_dir = tmppath / "components"
            components_dir.mkdir()

            # Create component subdirectories
            (components_dir / "component1").mkdir()
            (components_dir / "component2").mkdir()

            # Create building_blocks file
            blocks_file = components_dir / "building_blocks.yaml"
            blocks_file.write_text("- name: Block 1\n- name: Block 2\n")

            result = scan_project_directory(tmppath)

            # Should find components
            assert len(result['components']) == 2
            assert str(components_dir / "component1") in result['components']
            assert str(components_dir / "component2") in result['components']

            # Should find building_blocks
            assert result['building_blocks'] == str(blocks_file)

            # Should also populate component_breakdown alias
            assert result['component_breakdown'] == str(blocks_file)

    def test_scan_with_specifications(self):
        """Test scanning directory with specification files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create specifications directory
            specs_dir = tmppath / "specifications"
            specs_dir.mkdir()

            # Create spec files
            project_spec = specs_dir / "project_spec.md"
            project_spec.write_text("# Project Specification\n")

            tech_spec = specs_dir / "technical_spec.md"
            tech_spec.write_text("# Technical Specification\n")

            result = scan_project_directory(tmppath)

            # Should find specs
            assert result['project_spec'] == str(project_spec)
            assert result['technical_spec'] == str(tech_spec)


# ============================================================================
# Test 2: Error Handling Improvements (Priority 2)
# ============================================================================

class TestErrorHandlingImprovements:
    """Verify error handling uses specific exception types."""

    def test_count_building_blocks_handles_missing_file(self):
        """Verify count_building_blocks handles missing files gracefully."""
        result = count_building_blocks("/nonexistent/file.yaml")
        assert result == 0, "Should return 0 for missing file"

    def test_count_building_blocks_handles_invalid_file(self):
        """Verify count_building_blocks handles invalid files gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Write invalid content
            f.write("\x00\x01\x02\x03")  # Binary garbage
            f.flush()

            try:
                result = count_building_blocks(f.name)
                assert result == 0, "Should return 0 for unreadable file"
            finally:
                Path(f.name).unlink()

    def test_count_sprints_handles_missing_file(self):
        """Verify count_sprints handles missing files gracefully."""
        result = count_sprints("/nonexistent/sprint.md")
        assert result == 0, "Should return 0 for missing file"

    def test_find_most_recent_output_handles_missing_directory(self):
        """Verify _find_most_recent_output handles missing directory gracefully."""
        result = _find_most_recent_output(Path("/nonexistent/directory"), 0.0)
        assert result is None, "Should return None for missing directory"

    def test_find_most_recent_output_handles_permission_error(self):
        """Verify _find_most_recent_output handles permission errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create a directory with no read permissions (on Unix systems)
            if hasattr(tmppath, 'chmod'):
                test_dir = tmppath / "no_read"
                test_dir.mkdir()
                test_dir.chmod(0o000)

                try:
                    # Should handle permission error gracefully
                    result = _find_most_recent_output(tmppath, 0.0)
                    # Result could be None or the directory with no read perms
                    assert result is None or isinstance(result, Path)
                finally:
                    # Restore permissions for cleanup
                    test_dir.chmod(0o755)

    def test_error_handling_with_valid_yaml(self):
        """Verify error handling works correctly with valid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- name: Component 1\n- name: Component 2\n- name: Component 3\n")
            f.flush()

            try:
                result = count_building_blocks(f.name)
                assert result == 3, "Should correctly count building blocks in valid YAML"
            finally:
                Path(f.name).unlink()


# ============================================================================
# Test 3: Legacy Code Removal (Priority 8)
# ============================================================================

class TestLegacyCodeRemoval:
    """Verify unused legacy aliases were removed."""

    def test_paper_aliases_removed(self):
        """Verify PaperMetadata, PaperFiles, PaperResult were removed."""
        # These should NOT exist in models module
        assert not hasattr(models, 'PaperMetadata'), \
               "PaperMetadata alias should be removed"
        assert not hasattr(models, 'PaperFiles'), \
               "PaperFiles alias should be removed"
        assert not hasattr(models, 'PaperResult'), \
               "PaperResult alias should be removed"

    def test_project_classes_still_exist(self):
        """Verify the actual ProjectMetadata, ProjectFiles, ProjectResult still exist."""
        assert hasattr(models, 'ProjectMetadata'), \
               "ProjectMetadata should still exist"
        assert hasattr(models, 'ProjectFiles'), \
               "ProjectFiles should still exist"
        assert hasattr(models, 'ProjectResult'), \
               "ProjectResult should still exist"

        # Verify they're usable
        assert callable(models.ProjectMetadata)
        assert callable(models.ProjectFiles)
        assert callable(models.ProjectResult)


# ============================================================================
# Integration Test
# ============================================================================

class TestRefactoringIntegration:
    """Integration tests to verify refactoring didn't break functionality."""

    def test_full_project_scan_workflow(self):
        """Test complete project scanning workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create a realistic project structure
            (tmppath / "specifications").mkdir()
            (tmppath / "specifications" / "project_spec.md").write_text("# Project")

            (tmppath / "research").mkdir()
            (tmppath / "research" / "market_research.md").write_text("# Market Research")

            (tmppath / "analysis").mkdir()
            (tmppath / "analysis" / "feasibility_analysis.md").write_text("# Feasibility")

            (tmppath / "planning").mkdir()
            (tmppath / "planning" / "sprint_plan.md").write_text("## Sprint 1\n## Sprint 2\n")

            (tmppath / "components").mkdir()
            (tmppath / "components" / "building_blocks.yaml").write_text("- name: Block1\n- name: Block2\n")
            (tmppath / "components" / "comp1").mkdir()

            (tmppath / "diagrams").mkdir()
            (tmppath / "diagrams" / "architecture.png").write_text("fake image")

            (tmppath / "SUMMARY.md").write_text("# Summary")

            # Scan the directory
            result = scan_project_directory(tmppath)

            # Verify all fields populated correctly
            assert result['project_spec'] is not None
            assert result['market_research'] is not None
            assert result['feasibility_analysis'] is not None
            assert result['sprint_plan'] is not None
            assert result['building_blocks'] is not None
            assert result['component_breakdown'] is not None  # Alias
            assert result['summary'] is not None
            assert len(result['components']) == 1
            assert len(result['diagrams']) == 1

            # Verify paths are correct
            assert 'project_spec.md' in result['project_spec']
            assert 'market_research.md' in result['market_research']
            assert 'building_blocks.yaml' in result['building_blocks']
            assert 'building_blocks.yaml' in result['component_breakdown']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
