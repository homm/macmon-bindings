# MacmonSwift

Swift wrapper for the [macmon](https://github.com/vladkens/macmon) C API that copies FFI data into Swift structs.

## Build

Run Swift Package Manager commands from the repository root, where `Package.swift` is located.

By default, Swift Package Manager downloads the prebuilt `CMacmon.xcframework` from the URL configured in `Package.swift`.

For local builds, assuming the app, `macmon-bindings`, and `macmon` are in sibling directories, provide `MACMON_XCFRAMEWORK_PATH` with a path:

```sh
make -C ../macmon xcframework
MACMON_XCFRAMEWORK_PATH=../macmon/dist/CMacmon.xcframework swift build
```

For local Xcode development, create `MyApp.local.xcworkspace/contents.xcworkspacedata` with the app project and the local package, which overrides the remote package dependency:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Workspace version="1.0">
   <FileRef location="group:MyApp.xcodeproj"></FileRef>
   <FileRef location="group:../macmon-bindings"></FileRef>
</Workspace>
```

Use the Xcode workspace together with `MACMON_XCFRAMEWORK_PATH` when running `xcodebuild`:

```sh
make -C ../macmon xcframework
MACMON_XCFRAMEWORK_PATH=../macmon/dist/CMacmon.xcframework \
    xcodebuild -workspace MyApp.local.xcworkspace -scheme MyApp build
```

## Example

```swift
import MacmonSwift

let sampler = try Sampler()
let info = try Macmon.socInfo()
let metrics = try sampler.metrics()

print(info.chipName)
print(metrics.chipPower)
print(metrics.mediaPower)
```
