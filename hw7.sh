for L in 5 10 20 40; do
	./hw-ach start
	./proc4.py &
	./proc3.py $L &
	./proc2.py &
	./proc1.py &
	jobs
	wait `jobs -p 1`
	kill `jobs -p`
	jobs
	mv output/output.csv output/L$L.csv
done
