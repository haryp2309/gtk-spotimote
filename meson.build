project('test')

# Add a reference to the compiler to use
blueprint_compiler = find_program('blueprint-compiler')

# The blueprint files to be converted
blueprint_files = files(
    '../ui/bo.blp'
)

ui_files = []

foreach blueprint_file : blueprint_files
  path_as_string = '@0@'.format(blueprint_file)
  filename = path_as_string.split('/')[-1]

  ui_file = custom_target(path_as_string.underscorify(),
    input: blueprint_file,
    output: filename.replace('.blp', '.ui'),
    command: [blueprint_compiler, 'compile', '--output', '@OUTPUT@', '@INPUT@'])
  ui_files += ui_file
endforeach


gnome.compile_resources('sample',
  'sample.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: [ui_files]
)