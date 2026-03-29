# MacmonSwift

Swift wrapper for the Rust `macmon` library.

## Layout

- `../../dist/CMacmon.xcframework`: packaged `libmacmon.dylib` plus public headers produced by the core repository build
- `MacmonSwift`: safe Swift wrapper that copies FFI values into Swift structs

## Build

Build the core xcframework first:

```sh
make xcframework
```

Then build the Swift package:

```sh
cd bindings/swift
swift build
```

The packaged artifact is written to `dist/CMacmon.xcframework` in the repository root.

## Release archive

If a GitHub release includes `CMacmon.xcframework-<version>.zip`, you can use that artifact instead of
building Rust locally. Unpack the archive so that `dist/CMacmon.xcframework` exists in the repository root, then
build the Swift package as usual:

```sh
unzip /path/to/CMacmon.xcframework-<version>.zip -d .
cd bindings/swift
swift build
```

This package uses `binaryTarget(path:)`, so the xcframework must exist on disk. By default it looks in
`../../dist/CMacmon.xcframework`.

## Xcode

`bindings/swift` can be added to Xcode as a local Swift package. The package depends on the prebuilt
`../../dist/CMacmon.xcframework`, so build that artifact before opening or building an app target:

```sh
make xcframework
open ../MenuStats/StillCore.xcodeproj
```

Unlike the previous `libmacmon.dylib` workflow, the app target does not need a custom copy/sign script.
Xcode embeds the dynamic library from the xcframework through the package dependency.

## Example

```swift
import MacmonSwift

let sampler = try Sampler()
let info = try Macmon.socInfo()
let metrics = try sampler.metrics()

print(info.chipName)
print(metrics.power.package)
```
