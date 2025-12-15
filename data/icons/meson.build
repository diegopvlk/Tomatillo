application_id = 'io.github.diegopvlk.Tomatillo'

# ----------------------------------------------------------------------
# Existing app icons
# ----------------------------------------------------------------------
scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(application_id)),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)
