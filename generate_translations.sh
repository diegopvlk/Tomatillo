#!/bin/bash
OUTPUT="po/io.github.diegopvlk.Tomatillo.pot"
PACKAGE_NAME="io.github.diegopvlk.Tomatillo"
ENCODING="UTF-8"
LANGUAGE_BLP="--language=JavaScript"
LINGUAS_FILE="po/LINGUAS"

grep -v '\.blp$' po/POTFILES.in > /tmp/POTFILES_TOMATILLO
grep '\.blp$' po/POTFILES.in > /tmp/POTFILES_TOMATILLO.blp

# create pot
xgettext --files-from=/tmp/POTFILES_TOMATILLO \
         --output="$OUTPUT" --package-name="$PACKAGE_NAME" \
         --from-code="$ENCODING" --add-comments \
         --keyword=_ --keyword=C_:1c,2

# joint pot
xgettext --files-from=/tmp/POTFILES_TOMATILLO.blp \
         --output="$OUTPUT" --package-name="$PACKAGE_NAME" \
         --from-code="$ENCODING" --add-comments \
         --keyword=_ --keyword=C_:1c,2 \
         $LANGUAGE_BLP \
         --join-existing


rm /tmp/POTFILES_TOMATILLO /tmp/POTFILES_TOMATILLO.blp

sed -i 's/charset=CHARSET/charset=UTF-8/g' $OUTPUT

grep '^' "$LINGUAS_FILE" | while read -r lang_file; do
    msgmerge --previous --backup=none --update "po/${lang_file}.po" "$OUTPUT"
done