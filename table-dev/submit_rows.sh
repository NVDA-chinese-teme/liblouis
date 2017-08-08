WORKING_FILE=${1}
DICTIONARY=${2}
BASE_TABLE=${3}
RULE_GREP="^[ \t]*[+-]\?\(nocross\|syllable\*\|word\|begword\|endword\)"
set -e
set -x
if [ -e $WORKING_FILE ];  then
	cat $WORKING_FILE | grep -v "^$$" | grep -v "^#" > tmp || true
	mv tmp $WORKING_FILE
	if cat $WORKING_FILE | grep -v "$RULE_GREP" > tmp; then
		bash wrap_python.sh submit_rows.py -d $DICTIONARY -t $BASE_TABLE tmp
		cat $WORKING_FILE | grep "$RULE_GREP" > tmp || true
		mv tmp $WORKING_FILE
	else
		rm -f tmp
	fi
	[ -s $WORKING_FILE ] || rm $WORKING_FILE
fi
