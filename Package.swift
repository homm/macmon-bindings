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
    url: "https://github.com/homm/macmon/releases/download/v0.7.2/CMacmon.xcframework-v0.7.2.zip",
    checksum: "1cdcbb9bde1c035b1a9b767e7182afa5bc12f0f2472e1938cb7533fa3a70ea4a"
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
