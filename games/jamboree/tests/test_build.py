"""Packaging safety and portable-toolchain checks; no game files or keys."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME / 'scripts'))
import build_jamboree as build


class BuildTests(unittest.TestCase):
    def test_tooling_checksums(self):
        build.verify_prebuilt()

    def test_rejects_modified_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exefs = root / 'extract/v458752/ExeFS'
            exefs.mkdir(parents=True)
            for name in ('main', 'subsdk0', 'sdk'):
                (exefs / name).write_bytes(b'NSO0' + bytes(100))
            with self.assertRaisesRegex(ValueError, 'original ExeFS hash mismatch: main'):
                build.verify_originals(root)

    def test_refuses_to_replace_working_app(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'working.app'
            output.mkdir()
            marker = output / 'keep'
            marker.write_text('existing user app')
            with self.assertRaisesRegex(ValueError, 'output exists'):
                build.package(Path(tmp), Path(tmp), output, 'en-US')
            self.assertEqual(marker.read_text(), 'existing user app')

    def test_source_staging_preserves_generated_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            source = build.stage(work)
            table = source / f'dm/games/{build.TITLE}/c1_full.tsv'
            table.write_text('generated locally')
            build.stage(work)
            self.assertEqual(table.read_text(), 'generated locally')
            self.assertTrue((source / 'dm/tools/nx_extract/Program.cs').is_file())
            self.assertTrue((source / 'dm/gfx/tools/dmsh_xlate_bin/dmsh_xlate').is_file())
            chain = subprocess.check_output([sys.executable, str(source / 'dm/gfx/tools/dmsh_chain.py')], text=True).strip()
            self.assertEqual(chain, 'e6e2d522054e')

    def test_packaging_rejects_wrong_game_shader_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            source = build.stage(work)
            libraries = work / 'shader/cache/b-e6e2d522054e'
            libraries.mkdir(parents=True)
            (libraries / 'inputs.tsv').write_text('game\t0100000000000000\ninputs\twrong\n')
            with mock.patch.object(build, 'verify_originals', return_value={}):
                with self.assertRaisesRegex(ValueError, 'shader library stamp differs'):
                    build.package(source, work, work / 'test.app', 'en-US')
            self.assertFalse((work / 'test.partial.app').exists())

    def test_input_links_follow_relocated_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs, work = root / 'originals', root / 'build'
            inputs.mkdir(); work.mkdir()
            original = inputs / 'base.nsp'
            original.write_bytes(b'synthetic container')
            result = build.link_inputs(inputs, work)
            self.assertEqual((result / original.name).resolve(), original)
            original.unlink()
            (inputs / 'update.nsp').write_bytes(b'synthetic update')
            build.link_inputs(inputs, work)
            self.assertFalse((result / 'base.nsp').is_symlink())
            self.assertTrue((result / 'update.nsp').is_symlink())

    def test_build_caches_stay_in_work_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            env = build.environment(work)
            for key in ('TMPDIR', 'NUGET_PACKAGES', 'DOTNET_CLI_HOME'):
                self.assertTrue(Path(env[key]).is_relative_to(work))
                self.assertTrue(Path(env[key]).is_dir())

    def test_rejects_unsupported_build_before_rewrite(self):
        path = GAME / 'third_party/nxnative/build_ipa_from_nsp.py'
        spec = importlib.util.spec_from_file_location('nsp_builder_test', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'keys').write_bytes(b'synthetic')
            # Exercise main's title gate using a synthetic container inventory.
            with mock.patch.object(module, 'find_repo', return_value=GAME / 'runtime'), \
                 mock.patch.object(module, 'apple_silicon', return_value=True), \
                 mock.patch.object(module, 'scan_nsps', return_value=(0x0100000000000000, {})):
                args = module.parse_args([str(root), '-k', str(root / 'keys'), '--platform', 'mac', '-p', 'v458752'])
                sys.path.insert(0, str(GAME / 'runtime/games'))
                sys.path.insert(0, str(GAME / 'runtime/tools'))
                with self.assertRaisesRegex(module.BuildError, 'supports only Super Mario Party Jamboree'):
                    module.main(args)


if __name__ == '__main__':
    unittest.main()
