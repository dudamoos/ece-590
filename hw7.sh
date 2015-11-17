./hw-ach start
./proc4.py &
./proc3.py &
./proc2.py &
./proc1.py &
jobs
wait `jobs -p 1`
kill `jobs -p`
jobs
