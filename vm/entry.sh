#!/usr/bin/env bash

###################################################
# THIS IS NOT A CHALLENGE, IS THE SETUP OF THE VM #
###################################################

# podman ps is used to avoid podman compose crash on first run
podman ps &> /dev/null


if [[ "$1" == "prebuild" ]]; then
    podman --log-level=info system service --time=0 &>> /home/oasis/podman.log &
    # Only with this for loop we can exit internally from the loop
    for path in $(find /root/ -maxdepth 1 -mindepth 1 -type d); do
        if [[ -f "$path/compose.yml" || -f "$path/compose.yaml" || -f "$path/docker-compose.yml" || -f "$path/docker-compose.yaml" ]]; then
            cd $path
            echo "Building $path"
            podman compose build
            EXITCODE=$?
            echo "Build of $path exited with $EXITCODE"
            if [[ "$EXITCODE" != 0 ]]; then
                echo "Failed to build $path"
                exit $EXITCODE
            fi
        fi
    done

    # Firegex installation
    cd /
    git clone https://github.com/Pwnzer0tt1/firegex; cd firegex
    git checkout `git tag --sort=committerdate | tail -1`
    #Frontend build
    cd frontend
    bun i; bun run build

    mv dist ../backend/; cd ../backend; mv dist frontend
    
    # Backend build
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt --no-warn-script-location
    g++ binsrc/nfqueue.cpp -o modules/cppqueue -O3 -lnetfilter_queue -pthread -lpcre2-8 -ltins -lmnl -lnfnetlink
    g++ binsrc/proxy.cpp -o modules/proxy -O3 -pthread -lboost_system -lboost_thread -lpcre2-8

    echo "Prebuild execution done"
    exit 0
fi
if [[ "$1" == "entry" ]]; then
    podman --log-level=info system service --time=0 &>> /home/oasis/podman.log &
    
    cd /firegex/backend
    HEX_SET_PSW=`echo -n "$TOKEN" | xxd -p` python3 app.py DOCKER &> /var/log/firegex.log &
    cd /root

    TEAM_ID=$(ip a | grep -oP '((?<=)10.60.+.1\/24(?=))' | cut -d'.' -f3)
    # Set up network
    ip link set eth0 name game
    ip route add default via 10.60.$TEAM_ID.250

    cat <<EOF > /etc/sudoers
Defaults   !visiblepw

Defaults    always_set_home
Defaults    match_group_by_gid

Defaults    always_query_group_plugin

Defaults    env_reset
Defaults    env_keep =  "COLORS DISPLAY HOSTNAME HISTSIZE KDEDIR LS_COLORS"
Defaults    env_keep += "MAIL QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE"
Defaults    env_keep += "LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES"
Defaults    env_keep += "LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE"
Defaults    env_keep += "LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY"

Defaults    secure_path = /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/var/lib/snapd/snap/bin
root	ALL=(ALL) 	ALL
%wheel	ALL=(ALL)	NOPASSWD: ALL
EOF
    mkdir -p /var/run/sshd
    ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
    /usr/sbin/sshd -D -E /var/log/sshd.log &
    SSDPID=$!

    find /root/ -maxdepth 1 -mindepth 1 -type d -print0 | while read -d $'\0' path
    do
        if [[ -f "$path/compose.yml" || -f "$path/compose.yaml" || -f "$path/docker-compose.yml" || -f "$path/docker-compose.yaml" ]]; then
            cd $path
            if [[ -f "$path/predeploy.sh" ]]; then
                echo "Executing predeploy.sh"
                bash predeploy.sh
            fi
            podman compose up -d --build
        fi
    done

    trap "kill $SSDPID" EXIT
    tail -f /dev/null
    
fi

# Pre Deploy script can be useful to run some commands before the deployment of the services
# Eg.

# #!/usr/bin/bash
# cd $(dirname "$(readlink -f $0)")
# if [[ ! -f ".env" ]]; then
#     echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
# fi

#To generate an .env file with a random SECRET_KEY different for each team

