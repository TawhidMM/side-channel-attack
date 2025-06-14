/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;
/* Find the L3 size by running `getconf -a | grep CACHE` */
const LLCSIZE = 16 * 1024 * 1024;
/* Collect traces for 10 seconds; you can vary this */
const TIME = 10000;
/* Collect traces every 10ms; you can vary this */
const P = 10; 

function sweep(P) {
    /*
     * Implement this function to run a sweep of the cache.
     * 1. Allocate a buffer of size LLCSIZE.
     * 2. Read each cache line (read the buffer in steps of LINESIZE).
     * 3. Count the number of times each cache line is read in a time period of P milliseconds.
     * 4. Store the count in an array of size K, where K = TIME / P.
     * 5. Return the array of counts.
     */
    const K = TIME / P;
    const buffer = new Uint8Array(LLCSIZE);
    const counts = new Array(K).fill(0);

    const startTime = performance.now();
    let segmentStart = startTime;

    let segmentIndex = 0;

   while ((performance.now() - startTime) < TIME) {
        // Perform one cache sweep
        for (let i = 0; i < buffer.length; i += LINESIZE) {
            let value = buffer[i]; // Access each cache line
        }

        // Track how many sweeps were completed in current segment
        const now = performance.now();
        if ((now - segmentStart) >= P) {
            segmentIndex++;
            if (segmentIndex >= K) break;
            segmentStart += P;
        }

        counts[segmentIndex]++;
    }

    return counts;
}   

self.addEventListener('message', function(e) {
    /* Call the sweep function and return the result */
    if (e.data === "start") {
        const P = 5;

        self.postMessage(sweep(P));
    }
});