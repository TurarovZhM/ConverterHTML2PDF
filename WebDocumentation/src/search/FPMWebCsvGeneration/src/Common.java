import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FileUtils;
import org.jsoup.Jsoup;

public class Common {

	public static List<CsvValue> generateCsvValueList(File f)
			throws IOException {
		String originaltext = Jsoup.parse(FileUtils.readFileToString(f)).text()
				.toLowerCase();
		String regex = "[\"\\\\/!;,`~=:\'^.*?<>&(){}@#|%-\\\\$]";
		String text = originaltext.replaceAll(regex, " ");
		text = text.replaceAll("\\s+", " ").trim();
		String sp[] = text.split(" ");
		sp = removeStopWords(sp);
		Arrays.sort(sp);
		sp = removeDuplicates(sp);
		BoyerMoore bm = new BoyerMoore("");
		Map<String, ArrayList<Integer>> wordPositionInHtml = new HashMap<String, ArrayList<Integer>>();
		ArrayList<Integer> wordPositionList = null;
		ArrayList<String> documentPathList = null;
		// returns positions where a particular word lies in the document
		List<CsvValue> csvValueList = new ArrayList<CsvValue>();
		CsvValue csvValue = new CsvValue();
		// todo: logic needs to be changed to match with more than one html file
		Map<Integer, Integer> documentId;
		List<WordPositions> wordPosList = new ArrayList<WordPositions>();
		WordPositions wordPositions = new WordPositions();
		for (String s : sp) {
			if (s.length() > 1) {// removing the words whose length is 1
				bm = new BoyerMoore(s);
				int i = 0;
				int wordPositionArray[] = bm.search(originaltext);
				Integer[] newArray = new Integer[wordPositionArray.length];
				documentPathList = new ArrayList<String>();
				for (int value : wordPositionArray) {
					newArray[i++] = Integer.valueOf(value);
					documentPathList.add(f.getAbsolutePath());
				}
				wordPositionList = new ArrayList<Integer>(
						Arrays.asList(newArray));
				wordPosList = new ArrayList<WordPositions>();
				csvValue = new CsvValue();
				csvValue.setWord(s);
				csvValue.setNoOfDocumentsContainingThisWord(1);
				documentId = new HashMap<Integer, Integer>();
				documentId.put(1, wordPositionList.size());
				csvValue.setDocumentId(documentId);
				for (Integer wordPosition : wordPositionList) {
					wordPositions = new WordPositions();
					wordPositions.setPosition(wordPosition);
					wordPosList.add(wordPositions);
				}
				csvValue.setWordPositions(wordPosList);
				csvValueList.add(csvValue);
				wordPositionInHtml.put(s, (wordPositionList));
			}
		}
		System.out.println(wordPositionInHtml);
		return csvValueList;

	}

	/**
	 * Two csv files are generated.
	 * 
	 * 1st csv:(look into writeDocumentNameToCsvFile() function) CSV format:
	 * index of 1st document, absolute path of the 1st document, ... Eg:
	 * 1,/u/b/basnet/test.html,2,/u/b/basnet/bind.html,.........
	 * 
	 * 2nd csv:(look into writeToCsvFile() function) CSV format: word, no. of
	 * documents that contain this word, index of 1st document containing this
	 * word, no. of positions the word is in the 1st document, position 1,
	 * position 2, ............,index of 2nd document containing this word, no.
	 * of positions the word is in the 2nd document, position 1, position 2,
	 * ......, followed by new line for every next word Repeat the above
	 * 
	 * Eg: hello,2,1,2,100,150,4,5,13,100,505,606,700, niks,1,60,3,101,202,303,
	 * so on...............
	 * *****/

	public static void writeToCsvFile(List<CsvValue> csvValueList,
			String filePath) {
		try {
			FileWriter searchInformationWriter = new FileWriter(filePath);
			for (CsvValue csvValue : csvValueList) {
				searchInformationWriter.append(csvValue.getWord());
				searchInformationWriter.append(',');
				searchInformationWriter.append(Integer.toString(csvValue
						.getNoOfDocumentsContainingThisWord()));
				searchInformationWriter.append(',');
				for (Integer docId : csvValue.getDocumentId().keySet()) {
					searchInformationWriter.append(Integer.toString(docId));
					searchInformationWriter.append(',');
					searchInformationWriter.append(Integer.toString(csvValue
							.getDocumentId().get(docId)));
					searchInformationWriter.append(',');
					for (WordPositions wordPosition : csvValue
							.getWordPositions()) {
						searchInformationWriter.append(Integer
								.toString(wordPosition.getPosition()));
						searchInformationWriter.append(',');
					}
				}
				searchInformationWriter.append('\n');
			}
			// generate whatever data you want
			searchInformationWriter.flush();
			searchInformationWriter.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Writes document names and their index
	 * */
	public static void writeDocumentNameToCsvFile(
			List<String> documentNameList, String filePath) {
		try {
			FileWriter documentNameListWriter = new FileWriter(filePath);
			int index = 1;
			for (String documentName : documentNameList) {
				documentNameListWriter.append(Integer.toString(index));
				documentNameListWriter.append(',');
				documentNameListWriter.append(documentName);
				documentNameListWriter.append('\n');
				index++;
			}
			// generate whatever data you want
			documentNameListWriter.flush();
			documentNameListWriter.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	// Create an array with all unique elements
	public static String[] removeDuplicates(String[] A) {
		if (A.length < 2)
			return A;
		int j = 0;
		int i = 1;
		while (i < A.length) {
			if (A[i].equals(A[j])) {
				i++;
			} else {
				j++;
				A[j] = A[i];
				i++;
			}
		}
		String[] B = Arrays.copyOf(A, j + 1);
		return B;
	}

	/**
	 * removes stop words from given array of text
	 * 
	 * @return array of string without stop words
	 * */
	public static String[] removeStopWords(String[] text) {
		List<String> wordList = new ArrayList<String>();
		String stopWords[] = { "a", "about", "above", "above", "across",
				"after", "afterwards", "again", "against", "all", "almost",
				"alone", "along", "already", "also", "although", "always",
				"am", "among", "amongst", "amoungst", "amount", "an", "and",
				"another", "any", "anyhow", "anyone", "anything", "anyway",
				"anywhere", "are", "around", "as", "at", "back", "be",
				"became", "because", "become", "becomes", "becoming", "been",
				"before", "beforehand", "behind", "being", "below", "beside",
				"besides", "between", "beyond", "bill", "both", "bottom",
				"but", "by", "call", "can", "cannot", "cant", "co", "con",
				"could", "couldnt", "cry", "de", "describe", "detail", "do",
				"done", "down", "due", "during", "each", "eg", "eight",
				"either", "eleven", "else", "elsewhere", "empty", "enough",
				"etc", "even", "ever", "every", "everyone", "everything",
				"everywhere", "except", "few", "fifteen", "fify", "fill",
				"find", "fire", "first", "five", "for", "former", "formerly",
				"forty", "found", "four", "from", "front", "full", "further",
				"get", "give", "go", "had", "has", "hasnt", "have", "he",
				"hence", "her", "here", "hereafter", "hereby", "herein",
				"hereupon", "hers", "herself", "him", "himself", "his", "how",
				"however", "hundred", "ie", "if", "in", "inc", "indeed",
				"interest", "into", "is", "it", "its", "itself", "keep",
				"last", "latter", "latterly", "least", "less", "ltd", "made",
				"many", "may", "me", "meanwhile", "might", "mill", "mine",
				"more", "moreover", "most", "mostly", "move", "much", "must",
				"my", "myself", "name", "namely", "neither", "never",
				"nevertheless", "next", "nine", "no", "nobody", "none",
				"noone", "nor", "not", "nothing", "now", "nowhere", "of",
				"off", "often", "on", "once", "one", "only", "onto", "or",
				"other", "others", "otherwise", "our", "ours", "ourselves",
				"out", "over", "own", "part", "per", "perhaps", "please",
				"put", "rather", "re", "same", "see", "seem", "seemed",
				"seeming", "seems", "serious", "several", "she", "should",
				"show", "side", "since", "sincere", "six", "sixty", "so",
				"some", "somehow", "someone", "something", "sometime",
				"sometimes", "somewhere", "still", "such", "system", "take",
				"ten", "than", "that", "the", "their", "them", "themselves",
				"then", "thence", "there", "thereafter", "thereby",
				"therefore", "therein", "thereupon", "these", "they", "thickv",
				"thin", "third", "this", "those", "though", "three", "through",
				"throughout", "thru", "thus", "to", "together", "too", "top",
				"toward", "towards", "twelve", "twenty", "two", "un", "under",
				"until", "up", "upon", "us", "very", "via", "was", "we",
				"well", "were", "what", "whatever", "when", "whence",
				"whenever", "where", "whereafter", "whereas", "whereby",
				"wherein", "whereupon", "wherever", "whether", "which",
				"while", "whither", "who", "whoever", "whole", "whom", "whose",
				"why", "will", "with", "within", "without", "would", "yet",
				"you", "your", "yours", "yourself", "yourselves", "the" };
		boolean isStopWord = false;
		for (String word : text) {
			isStopWord = false;
			for (int i = 0; i < stopWords.length; i++) {
				if (word.equalsIgnoreCase(stopWords[i])) {
					word = word.replaceAll(stopWords[i] + "\\s+", ""); // note
																		// this
																		// will
																		// remove
																		// spaces
																		// at
																		// the
					isStopWord = true; // end loop
					break;
				}
			}
			if (!isStopWord) {
				wordList.add(word);
			}
		}
		String[] array = new String[wordList.size()];
		wordList.toArray(array);
		return array;
	}
}
