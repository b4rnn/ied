#JSON BIN FILE
	JSON_FILE="$1"
	JSON_FILE_SIZE="$2"
	JSON_FILE_TYPE="$3"
#JSON BINS
	#PURGE PREVIOUS JSON BINS
		rm -rf ${PWD}"/pieces"
	#GENERATE JSON BINS
		#SINKS EXISTS
		if [[ -d ${PWD}"/pods" ]];then
			mkdir pieces && cd pieces && split -a 3 --numeric-suffixes=1 --additional-suffix=.json -l $JSON_FILE_SIZE ../$JSON_FILE bin_  && cd ..
		fi
		#NO SINKS EXISTS
		if [[ ! -d ${PWD}"/pods" ]];then
			mkdir pods && mkdir pieces && cd pieces && split -a 3 --numeric-suffixes=1 --additional-suffix=.json -l $JSON_FILE_SIZE ../$JSON_FILE bin_  && cd ..
		fi
		#mkdir pods && mkdir pieces && cd pieces && split -a 3 --numeric-suffixes=1 --additional-suffix=.json -l $JSON_FILE_SIZE ../$JSON_FILE bin_  && cd ..
#GET JSON BINS
for selected_json_file in  $(find ${PWD}"/pieces" -maxdepth 1 -type f); do
	#NANOBIN POD ID
		NANOBIN_VIRUALENV_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
	#NANOBIN DIRECTORY
		$(mkdir ${PWD}"/pods/${NANOBIN_VIRUALENV_UUID}")
		NANOBIN_VIRUALENV_POD_DIRECTORY=${PWD}"/pods/${NANOBIN_VIRUALENV_UUID}"
		echo $NANOBIN_VIRUALENV_POD_DIRECTORY
		#trap "echo 'INFO: Exited temporary shell.' >&2; rm --force --recursive '${NANOBIN_VIRUALENV_POD_DIRECTORY}'" EXIT
		#CREATE MODEL DIRECTORY IN VIRTUALENV
		 mkdir $NANOBIN_VIRUALENV_POD_DIRECTORY/model
	#POD VIRTUAL ENV
		virtualenv -p /usr/bin/python3 "${NANOBIN_VIRUALENV_POD_DIRECTORY}"
		. "${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/activate"
		# Install any required pip packages
		[ -r "$(pwd)/requirements.txt" ] && pip3 install --requirement "$(pwd)/requirements.txt"

		# copy apIs file into the nanopod
		cp -r "$(pwd)/nanobin.py" "$(pwd)/nanopod.py" "$selected_json_file" $NANOBIN_VIRUALENV_POD_DIRECTORY/bin/

		#update the default port [5000]  in nanopod.py  with a free port selected from range 
		declare -i FREE_PORT
		START_PORT=8000
		END_PORT=8200
		for i in $(seq $START_PORT $END_PORT); do
			if ! [[ $(sudo netstat -plnt | grep ":$i") ]]; then 
				FREE_PORT=$i
			elif [ "$i" == "$END_PORT" ]; then
				echo "no ports to use"
			fi
		done
		echo -e "SELECTED FREE PORT " $FREE_PORT $JSON_FILE_TYPE >> "ports.txt"
		sed -i -e "s/5000/${FREE_PORT}/g" ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/nanopod.py

		#update bin path with actual path
		sed -i -e "s/bin_path/""$(basename "$selected_json_file")""/g" ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/nanopod.py

		#CREATE NANOMODELS FROM JSON BINS
		python3 ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/nanobin.py --bin_path $selected_json_file  --bin_index $(basename "$selected_json_file" .json) --pod_path ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/

		#UPDATE NANOSINK FOR CONTAINERS MANAGEMENT
			echo -e "virtualenv -p /usr/bin/python3 "${NANOBIN_VIRUALENV_POD_DIRECTORY}"" >> "$(pwd)/start_containers.sh"
			echo -e ". "${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/activate"" >> "$(pwd)/start_containers.sh"
			echo -e "python3 ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/nanopod.py &" >> "$(pwd)/start_containers.sh"

		# START NANAPOD SCRIPT TO FIRE SELECTED PORT [RUN AS BACKGROUND PROCESS]
		python3 ${NANOBIN_VIRUALENV_POD_DIRECTORY}/bin/nanopod.py &

		#PURGE PREVIOUSLY USED JSON BIN
		rm -rf $selected_json_file
done
#SYSTEM RESETS
	#RELOAD NGINX SERVER
