# Application-level True Random Number Generator

We've implemented 9.5 Mbit/second TRNG (True Random Number Generator) based on a scientific article.

## Advantage of Rando TRNG

This TRNG generates output bit by bit - therefore it can be adjusted to any practical needs (e.g. 8 bit words, 16 bit words, etc.).

### Comparing Rando with other TRNGs

| TRNG Type     | CPU Cycles         | Security                  | Entropy Source                                 | Requirements       |
|---------------|--------------------|---------------------------|------------------------------------------------|--------------------|
| Rando         | ~150 per bit       | Open-Source               | CPU frequency fluctuation, OS backgroung noise | OS                 |
| OS Kernel     | ~4500 for 64 bits  | Open-Source/ Close-Source | 100+ OS events                                 | OS                 |
| Environmental | ~60000 for 64 bits | Open-Source/ Close-Source | Physical                                       | Pereferial Devices |
| Hardware      | ~400 for 64 bits   | Close-Source              | Physical                                       | Chip itself        |

### SpeedTest Results

- Average result generating 9.5 Mbit/second of random bits. (Tested with implemented benchmark_trng_throughput() function)

## Implementation

### C++

Sustainable and actively maintained version of implementation packed following OOP principles. 

### Python

Deprecated demo version that, eventually, will be refreshed later.

## NIST 800.22

We successfully confirmed author's results of NIST 800.22 statistical test.
The results are attached in [finalAnalysisReport.txt](https://github.com/yepiiik/whitebox-trng/blob/master/finalAnalysisReport.txt) file.