fun() {
    x=($(python3.7 ghist.py --database /home/peter/.ghist.db ref $1))
    ${x[@]}
}
