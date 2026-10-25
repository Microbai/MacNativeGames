# Validation record

Date: **2026-10-25**. Game: **Super Mario Party Jamboree 2.3.0**, `0100965017338000`, `v458752`. Input NSO sizes, SHA-256 values and build IDs are recorded in [expected-2.3.0.json](../assets/expected-2.3.0.json).

Hardware: Apple M6 Mac mini (`Mac18,5`), Apple silicon / unified memory. OS: macOS **27.0.1 (26A434)**. This is the local test machine, not a performance promise for other Macs. Deployment target is macOS 26; macOS 26 itself has not been tested. iOS/iPadOS/visionOS were neither built nor played for this target.

## Automated checks

| Check | Result | What it establishes |
|---|---|---|
| Root `python -m unittest discover -s tests` | 331 passed | Existing repository source suite remains green |
| Game build tests | 8 passed | Original-input mismatch rejection, unsupported-title rejection, output preservation, source staging, external caches, compiler checksums |
| Synthetic discard translator tests | 2 passed | Void entry keeps side effects and early returns; correct storage write flag |
| Isolated native `t_vbuf` with Metal validation | 43 checks, 0 failed | Vertex buffer binding/invalidation behavior |
| Isolated native `t_geometry` with Metal validation | 127 checks, 0 failed | Geometry, transform feedback, discard-only vertex stores and instancing |

The GPU tests were rebuilt from **this game directory's copied source**, staged outside the checkout. No other game target supplied source, headers or compiler binaries. The translator chain computed by the staged source is `e6e2d522054e`; game shader inputs are `37da065929be`.

## Private build of this contribution

The isolated target was built against local original base XCI + 2.3.0 update NSP. Previously extracted original files were reused and their pinned NSO hashes checked; **all three NSO modules and 139 NROs were rewritten again** by the copied rewriter. The shader split was recreated from those private originals (25,693 shaders), matching shader-cache entries were reused, and both runtime binding tables were regenerated. No game-derived outputs enter the source tree.

The final arm64 host and launcher were built with the macOS 26 deployment target. The final app passed deep strict signature verification, and its build-info host hash was checked against the **signed** nested executable. The bundled host then ran for a 60-second headless smoke test using a private save copy: it entered `nnMain`, loaded shader inputs `37da065929be` and 24,814 uniform-read extent records, and reached frame 2,100 without exiting. This verifies startup and rendering submission from the packaged paths; it does not establish visual correctness for additional scenes or physical input behavior. A separate pre-packaging host smoke run lasted 90 seconds.

## Native play observations before contribution packaging

The same geometry-fix source was compiled into the local native app and exercised on the above Mac:

- Opening/title flow and character selection reached the plaza.
- Character selection switched Mario → Donkey Kong → Mario → Peach → Mario. The large stretched triangles were absent in the inspected character views.
- Plaza welcome close-up/dialog and wide view rendered the character meshes without the earlier stretching.
- The producer ran with rasterizer discard enabled and transform feedback off. A translated morph-shader check matched 24/24 output values and bounds. That shader-derived test is private and is not redistributed.
- A 300-frame plaza window had frame-time p50 **16.66 ms**, p95 **17.24 ms**; GPU p50 **4.03 ms**, p95 **4.97 ms**. This is a local steady-scene observation, not a full-game benchmark.
- Saved face-button layout was read as `label`. Physical controller presses were not exercised.
- The local packaged app passed deep strict signature verification both before and after launch.

Screenshots, translated shaders and saves used for local verification are not included in Git because they contain or derive from game content.

## Known limitations

- Full shader processing yielded **25,690 / 25,693** successful translations. Three existing failures report `Subgroup builtins are not available in this type of function` from SPIRV-Cross. Their scene coverage is unknown; they remain unresolved.
- One shader still reports an unrecognized binding kind. Many translation queries use defaults because this game's fact table does not answer them. Reaching the tested plaza does not establish correctness in other scenes.
- Some first-visit scenes paused or briefly showed white for **9–17 seconds**, then resumed rendering. Runtime shader compilation remains visible to the player; no claim of smooth first traversal is made.
- Full boards, all minigames, motion input, multiple physical controllers, long sessions, memory stability and save round trips have not been comprehensively verified.
- Only the pinned update is accepted. Other updates, DLC, mods, online features and compressed containers have not been validated.
- The app uses local ad-hoc signing. Distribution/notarization and operation on another Mac have not been tested.

## Reproduce without game content

From the repository root:

```sh
python3 -m unittest discover -s tests
make -C games/jamboree test
make -C games/jamboree test-gpu WORK=/path/to/private/Jamboree-gpu-tests
```

For the private full build, use the command in [README.md](../README.md). Logs stay under `<work>/input/0100965017338000_build/logs/`. Preserve the generated app's `build-info.json` and the existing `patched_v458752/build_src.sha256` when reporting an issue. Share a redacted log and version identifiers; do not upload game programs, shader source/libraries, keys or saves.
