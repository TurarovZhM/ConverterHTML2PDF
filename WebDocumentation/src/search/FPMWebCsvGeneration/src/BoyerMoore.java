import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.apache.commons.lang3.ArrayUtils;

public class BoyerMoore {
    private final int BASE;
    private int[] occurrence;
    private String pattern;

    public BoyerMoore(String pattern) {
        this.BASE = 256;
        this.pattern = pattern;

        occurrence = new int[BASE];
        for (int c = 0; c < BASE; c++)
            occurrence[c] = -1;
        for (int j = 0; j < pattern.length(); j++){
            occurrence[pattern.charAt(j)] = j;
           // System.out.println(pattern.charAt(j));
        }
    }

    public int[] search(String text) {
    	int n = text.length();
    	int m = pattern.length();
        int skip;
        List<Integer> patternCount = new ArrayList<Integer>();
        for (int i = 0; i <= n - m; i += skip) {
            skip = 0;
            for (int j = m-1; j >= 0; j--) {
                if (pattern.charAt(j) != text.charAt(i+j)) {
                    skip = Math.max(1, j - occurrence[text.charAt(i+j)]);
                    break;
                }
            }
            if (skip == 0) {
            	skip+=m;
            	patternCount.add(i);
            }
        }
        return ArrayUtils.toPrimitive(patternCount.toArray(new Integer[patternCount.size()]));
    }
}
