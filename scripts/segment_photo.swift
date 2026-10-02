// Segment the portrait photo and locate the face with Apple's Vision framework.
// Usage: swift scripts/segment_photo.swift /path/to/photo.jpg /output/dir
// Writes subject.png, person.png (8-bit masks, photo size) and face.json.
import CoreImage
import Foundation
import ImageIO
import Vision

let args = CommandLine.arguments
guard args.count == 3 else {
    FileHandle.standardError.write("usage: segment_photo.swift PHOTO OUTDIR\n".data(using: .utf8)!)
    exit(2)
}
let input = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2], isDirectory: true)
try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

guard let source = CGImageSourceCreateWithURL(input as CFURL, nil),
      let raw = CGImageSourceCreateImageAtIndex(source, 0, nil) else { fatalError("Cannot read \(input.path)") }
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any]
let orientation = CGImagePropertyOrientation(rawValue: (props?[kCGImagePropertyOrientation] as? UInt32) ?? 1) ?? .up
let oriented = CIImage(cgImage: raw).oriented(orientation)
let context = CIContext()
let upright = context.createCGImage(oriented, from: oriented.extent)!
let width = Double(upright.width), height = Double(upright.height)
let handler = VNImageRequestHandler(cgImage: upright, options: [:])
let gray = CGColorSpaceCreateDeviceGray()

// Subject lifting gives a crisp outline of hair and shoulders.
let subject = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([subject])
if let result = subject.results?.first {
    let buffer = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
    try context.writePNGRepresentation(of: CIImage(cvPixelBuffer: buffer), to: outDir.appendingPathComponent("subject.png"),
                                       format: .L8, colorSpace: gray)
}

// Person segmentation keeps more of the loose hair strands.
let person = VNGeneratePersonSegmentationRequest()
person.qualityLevel = .accurate
person.outputPixelFormat = kCVPixelFormatType_OneComponent8
try handler.perform([person])
if let buffer = person.results?.first?.pixelBuffer {
    let mask = CIImage(cvPixelBuffer: buffer)
    let scaled = mask.transformed(by: CGAffineTransform(scaleX: width / mask.extent.width, y: height / mask.extent.height))
    try context.writePNGRepresentation(of: scaled, to: outDir.appendingPathComponent("person.png"), format: .L8, colorSpace: gray)
}

// Pupils, eye outlines and the face box anchor relighting and eye balancing.
let landmarks = VNDetectFaceLandmarksRequest()
try handler.perform([landmarks])
var face: [String: Any] = ["width": width, "height": height]
if let found = landmarks.results?.first {
    let box = found.boundingBox
    face["box"] = [box.minX * width, (1 - box.maxY) * height, box.maxX * width, (1 - box.minY) * height]
    let size = CGSize(width: width, height: height)
    for (name, region) in [("leftPupil", found.landmarks?.leftPupil), ("rightPupil", found.landmarks?.rightPupil),
                           ("leftEye", found.landmarks?.leftEye), ("rightEye", found.landmarks?.rightEye),
                           ("medianLine", found.landmarks?.medianLine)] {
        if let region {
            face[name] = region.pointsInImage(imageSize: size).map { [Double($0.x), height - Double($0.y)] }
        }
    }
}
let data = try JSONSerialization.data(withJSONObject: face, options: [.prettyPrinted, .sortedKeys])
try data.write(to: outDir.appendingPathComponent("face.json"))
print("Wrote masks and face.json to \(outDir.path)")
