
#!/usr/bin/bash

if [ "$#" -ne 1 ]; then
    printf "\nPlease specify path to interposition.py "
    printf "(including interpose.py).  This will "
    printf "likely be in the deps folder sdn_fuzz/bin.\n"
else
    # provided path to interposition.
    python $1 --type=error --listen-on-addr=127.0.0.1:8888 --controller-addr=127.0.0.1:6633 --additional='{"failure_probability": .2}'
fi
