require "xcodeproj"

root = File.expand_path(__dir__)
project_path = File.join(root, "FinancialRiskMonitor.xcodeproj")
project = Xcodeproj::Project.new(project_path)

app_target = project.new_target(:application, "FinancialRiskMonitorApp", :ios, "16.0")
app_target.build_configurations.each do |config|
  config.build_settings["PRODUCT_BUNDLE_IDENTIFIER"] = "com.financialriskmonitor.app"
  config.build_settings["INFOPLIST_FILE"] = "App/Info.plist"
  config.build_settings["SWIFT_VERSION"] = "6.0"
  config.build_settings["TARGETED_DEVICE_FAMILY"] = "1,2"
  config.build_settings["SUPPORTED_PLATFORMS"] = "iphoneos iphonesimulator macosx"
  config.build_settings["MACOSX_DEPLOYMENT_TARGET"] = "13.0"
  config.build_settings["IPHONEOS_DEPLOYMENT_TARGET"] = "16.0"
end

group = project.main_group.new_group("FinancialRiskMonitorApp")
app_entry = group.new_file(File.join(root, "App", "FinancialRiskMonitorAppMain.swift"))
info = group.new_file(File.join(root, "App", "Info.plist"))
app_target.add_file_references([app_entry])

core_group = project.main_group.new_group("FinancialRiskMonitorCore")
core_files = Dir[File.join(root, "Sources", "FinancialRiskMonitorCore", "*.swift")].sort
core_refs = core_files.map { |file| core_group.new_file(file) }
app_target.add_file_references(core_refs)

app_target.build_phases.each do |phase|
  next unless phase.respond_to?(:files)
  phase.files.each do |build_file|
    build_file.settings = { "COMPILER_FLAGS" => "-D SWIFT_PACKAGE" } if build_file.file_ref && build_file.file_ref.path.to_s.include?("FinancialRiskMonitorCore")
  end
end

project.root_object.attributes["LastUpgradeCheck"] = "2700"
project.save

scheme = Xcodeproj::XCScheme.new
scheme.configure_with_targets(app_target, nil)
scheme_path = File.join(project_path, "xcshareddata", "xcschemes", "FinancialRiskMonitorApp.xcscheme")
FileUtils.mkdir_p(File.dirname(scheme_path))
scheme.save_as(project_path, "FinancialRiskMonitorApp", true)

puts "Generated #{project_path}"
