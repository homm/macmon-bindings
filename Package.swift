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
    url: "https://github.com/homm/macmon/releases/download/v0.7.3/CMacmon.xcframework-v0.7.3.zip",
    checksum: "364745111d6d96ce05a47ac7a7b7a639ef8e20e81edce8519393e8944da4806c"
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
