#STOP ALL CONTAINER PORTS
low=10000;
high=10300;
for i in `seq $low $high`; do
  lsof -i :$i | tail -n +2 | awk '{system("kill -s 9 " $2)}';
done

#DEACTIVATE NANOPODS IN THEIR RESPECTIVE SINKS [ENVS]
