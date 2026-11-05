// swift-tools-version: 5.9

import Foundation
import PackageDescription

let cMacmonTarget: Target

if let localPath = ProcessInfo.processInfo.environment["MACMON_XCFRAMEWORK_PATH"], !localPath.isEmpty {
  cMacmonTarget = .binaryTarget(
    name: "CMacmon",
    path: localPath
  )
} else {
  cMacmonTarget = .binaryTarget(
    name: "CMacmon",
    url: "https://github.com/homm/macmon/releases/download/capi-v0.10.0.1/CMacmon.xcframework-v0.10.0.1.zip",
    checksum: "8f55541930c8b0eac54c25324997b28c179e6ce8db318473ed1c503a7b626b10"
  )
}

let package = Package(
  name: "MacmonSwift",
  platforms: [
    .macOS(.v11),
  ],
  products: [
    .library(name: "MacmonSwift", targets: ["MacmonSwift"]),
  ],
  targets: [
    cMacmonTarget,
    .target(
      name: "MacmonSwift",
      dependencies: ["CMacmon"],
      path: "swift/Sources/MacmonSwift"
    ),
  ]
)
