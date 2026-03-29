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
    url: "https://github.com/homm/macmon/releases/download/v0.7.0/CMacmon.xcframework-v0.7.0.zip",
    checksum: "ce002405e52c2706be5ead3d1756591ba4de76aad91428c3bd578dd98b639697"
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
      path: "Sources/MacmonSwift"
    ),
  ]
)
