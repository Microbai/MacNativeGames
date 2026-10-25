# Locked shader compiler tooling

`dmsh_xlate/` is copied byte-for-byte from nxnative's `dm/gfx/tools/dmsh_xlate_bin` at commit `7861e7c1a9913e020600b1cc7f65132427e9cc50`. `SHA256SUMS` covers every file. The portable builder verifies those hashes before staging the tools.

This is a framework-dependent .NET 10 **shader translator**, not translated game shaders. Its macOS apphost launches the included DLLs on the build machine. It is not shipped inside the generated game app. See [source provenance](../../third_party/COPIES.md) and [third-party notices](../../THIRD_PARTY_NOTICES.md).

The matching translator source is `runtime/gfx/tools/dmsh_xlate`; its three shader-library dependencies are in `runtime/third_party/ryujinx`. The DLL fingerprints and embedded source hash are checked by `runtime/gfx/tools/dmsh_chain.lock`. Rebuilding the translator requires updating the lock and chain header, then rebuilding the game shader set and native host. Do not silently replace a locked DLL with another build.
