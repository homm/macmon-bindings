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
    url: "https://github.com/homm/macmon/releases/download/capi-v0.10.0/CMacmon.xcframework-v0.10.0.zip",
    checksum: "5e36809d9c91ef32d600ece13682ac87a4ca3e95f409b2b030295f1df624438a"
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
