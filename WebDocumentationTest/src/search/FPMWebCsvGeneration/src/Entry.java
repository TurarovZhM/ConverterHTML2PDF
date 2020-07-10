import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;


//TODO: Implement for more than one html documents
public class Entry {

	public static void main(String[] args) throws IOException,
			InterruptedException {
		// Todo: check if this logic is working with two html files first
		File makePath = new File("/u/b/basnet/WebDocumentation/"); // read from
																	// the
																	// location
																	// of make
																	// file i.e.
																	// the path
																	// of the
																	// file
																	// where
																	// this
																	// exectuable
																	// jar is
																	// written
		List<CsvValue> csvValueList = new ArrayList<CsvValue>();
		List<CsvValue> finalCsvValueList = new ArrayList<CsvValue>();
		List<CsvValue> mergedCsvValueList = new ArrayList<CsvValue>();
		List<CsvValue> tempCsvValueList = new ArrayList<CsvValue>();
		List<String> documentNameList = new ArrayList<String>();
		for (File f : makePath.listFiles()) {
			if (f.getName().endsWith(".html")) {
				//todo: logic needs to be changed to match with more than one html files
				tempCsvValueList = Common.generateCsvValueList(f);
				finalCsvValueList = new ArrayList<CsvValue>();
				mergedCsvValueList = new ArrayList<CsvValue>();
				List<String> oldWordList = new ArrayList<String>();
				List<String> newWordList = new ArrayList<String>();
				for (CsvValue csvValue : tempCsvValueList) {
					newWordList.add(csvValue.getWord());
				}
				if (oldWordList.size() <= 0) {// for the first time setting old
												// list value
					oldWordList = newWordList;
					finalCsvValueList = tempCsvValueList;
					System.out.println("finalCsvValueList-->"
							+ finalCsvValueList);
				} else {
					mergedCsvValueList.addAll(tempCsvValueList);
					oldWordList.addAll(newWordList);
					Collections.sort(oldWordList);
					for (String word : oldWordList) {
						for (int i = 0; i < mergedCsvValueList.size(); i++) {
							if (word.equalsIgnoreCase(mergedCsvValueList.get(i)
									.getWord())) {
								finalCsvValueList
										.add(mergedCsvValueList.get(i));
								System.out.println("finalCsvValueList-->"
										+ finalCsvValueList);
							}
						}
					}
				}
				documentNameList.add(f.getAbsolutePath());
			}
		}
		Common.writeDocumentNameToCsvFile(documentNameList,
				"/u/b/basnet/documentNameList.csv");
		Common.writeToCsvFile(finalCsvValueList,
				"/u/b/basnet/searchInformation.csv");
		// Common.writeToCsvFile(csvValueList);
	}
}