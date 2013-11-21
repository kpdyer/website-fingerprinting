Traffic Analysis Framework
==========================

This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail" [1].

Contact details
---------------

* website: https://kpdyer.com

Notes
-----

* Installed and tested on RHEL5
* Caching (via memcache) is disabled by default. Toggle ENABLE_CACHE in Datastore.py at your own risk.

Requirements
------------

* Required RHEL5 packages: ```mysql mysql-server memcached python-memcached MySQL-python python-devel gcc python-dpkt atlas atlas-devel lapack lapack-devel blas blas-devel glpk-devel g2clib-devel compat-libf2c-34 compat-gcc-34-g77```
* For Traffic Morphing install cvxopt-0.9 from source
* Python 2.4 or later (Installed on RHEL5 by default)
* WEKA (http://www.cs.waikato.ac.nz/ml/weka/)
* Liberatore and Levine [2] WebIdent 2 Traces (http://traces.cs.umass.edu/index.php/Network/Network)
* Herrmann et al. [3] MySQL Dataset (http://epub.uni-regensburg.de/11919)

### Getting started

1. Open config.py and set:
   * WEKA_ROOT to a directory that contains WEKA
   * PCAP_LOGS to the directory with extracted Liberatore and Levine pcap files
   * MYSQL_HOST/MYSQL_USER/MYSQL_PASSWD/MYSQL_DB settings for the Herrmann database
2. Execute "python main.py -h" to get help for runtime parameters
3. Output from main.py is placed the 'output' directory.
   Execute 'parseResultsFile.py' to interpret results.

References
----------
* [1] Dyer K.P., Coull S.E., Ristenpart T., Shrimpton T. Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail, To appear at IEEE Security and Privacy 2012
* [2] Marc Liberatore and Brian Neil Levine, Inferring the Source of Encrypted HTTP Connections. Proceedings of the 13th ACM Conference on Computer and Communications Security (CCS 2006)
* [3] Dominik Herrmann, Rolf Wendolsky, and Hannes Federrath. Website Fingerprinting: Attacking Popular Privacy Enhancing Technologies with the Multinomial Naive-Bayes Classiﬁer. In Proceedings of the ACM Workshop on Cloud Computing Security, pages 31–42, November 2009.
