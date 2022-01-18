def pairwise_median_slopes (spval, value_list):
    import numpy as np
    from math import sqrt
# Return the pairwise median slope and a significance flag
#
    ngood = np.count_nonzero(value_list != spval)
#    print("good values {}".format(ngood))
    slopes = np.empty(ngood*(ngood-1)//2) # int division OK
#    print("slopes to compute {}".format(ngood*(ngood-1)//2))
    k = 0
    n = value_list.size
    for i in range(0,n-1):
        if value_list[i] == spval: continue
        for j in range(i+1,n):
            if value_list[j] == spval: continue
            slopes[k] = (value_list[j] - value_list[i]) / (j - i)
            k += 1

    sorted_slopes=np.sort(slopes)
# (k+1) is the total number of slopes computed.  If odd, median is at
# index k/2 of the sorted array.  If even, median is average of values
# above and below k/2.
    if k % 2 == 0:
        median = sorted_slopes[k//2]
    else:
        median = 0.5 * (sorted_slopes[(k+1)//2] + \
                        sorted_slopes[(k-1)//2] )

    ru = round( (k + 1.96*sqrt(ngood*(ngood-1)*(2*ngood+5)/18.) )/2. + 1.) -1
    rl = round( (k - 1.96*sqrt(ngood*(ngood-1)*(2*ngood+5)/18.) )/2. )     -1
    if ru > k-1 or rl < 0:
        return (-1.e10, 0)

    signif = 0
    if sorted_slopes[rl] < 0 and sorted_slopes[ru] < 0:
        signif = -1
    elif sorted_slopes[rl] > 0 and sorted_slopes[ru] > 0:
        signif = 1
    return (median, signif)


