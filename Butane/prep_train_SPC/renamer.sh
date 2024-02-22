for i in {1..500}; do
  old_folder="but_Boltz_$i"
  new_folder="But_BoltzDist_SPC_$i"
  echo "Renaming: $old_folder to $new_folder"
  mkdir "$new_folder"
  cp "$old_folder"/* "$new_folder"
done
