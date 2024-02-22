for i in {0..499}; do
  old_folder="umbrella_$i"
  new_folder="restraint_$i"
  echo "Renaming: $old_folder to $new_folder"
  mkdir "$new_folder"
  cp "$old_folder"/* "$new_folder"
done
