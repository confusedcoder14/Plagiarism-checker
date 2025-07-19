from scipy.spatial.distance import cosine
from skimage import io, color, feature
from pathlib import Path
from udp import generate_digital_pattern, compare_patterns
from ocr import extract_text
from sentence_transformers import SentenceTransformer, util
from openai_model import compare_text_similarity, extract_similarity_value
import os
import streamlit as st

model = SentenceTransformer('all-MiniLM-L6-v2')

def scan_for_plagiarism(submission_folder, checkbok):
    submission_path = Path(submission_folder)
    result_log = []

    with st.spinner("Scanning for Plagiarism"):
        if not submission_path.exists() or not submission_path.is_dir():
            error_msg = f"Folder '{submission_path}' does not exist."
            st.error(error_msg)
            return error_msg

        submissions = list(submission_path.iterdir())
        st.success(f"Found {len(submissions)} submissions.")
        result_log.append(f"Found {len(submissions)} submissions.")

        text_list = [extract_text(os.path.join(submission_folder, sub)) for sub in submissions]
        excluded_docs = {}
        cp_list, pp_list, level4_list = [], [], []

        with st.expander("Live Processing"):
            for i in range(len(submissions)):
                if submissions[i] in excluded_docs: continue
                for j in range(i + 1, len(submissions)):
                    file1 = os.path.splitext(submissions[i].name)[0]
                    file2 = os.path.splitext(submissions[j].name)[0]

                    pattern1 = generate_digital_pattern(os.path.join(submission_folder, submissions[i]))
                    pattern2 = generate_digital_pattern(os.path.join(submission_folder, submissions[j]))

                    min_len = min(len(pattern1), len(pattern2))
                    pattern1 = pattern1[:min_len]
                    pattern2 = pattern2[:min_len]

                    similarity = compare_patterns(pattern1, pattern2)

                    if similarity > 0.95:
                        msg = f"\nLevel 1: Complete Plagiarism detected between {file1} and {file2}"
                        st.write(msg)
                        result_log.append(msg)
                        excluded_docs[submissions[j]] = True
                        cp_list.append((file1, file2))
                    elif similarity > 0.55:
                        text1, text2 = text_list[i], text_list[j]
                        if text1 and text2:
                            emb1, emb2 = model.encode(text1), model.encode(text2)
                            cos_sim = util.cos_sim(emb1, emb2).item()
                            if cos_sim >= 0.85:
                                msg = f"\nLevel 2: Complete Plagiarism between {file1} and {file2}"
                                cp_list.append((file1, file2))
                            else:
                                msg = f"\nLevel 2: Potential Plagiarism between {file1} and {file2} with UDP = {similarity*100:.2f}%, Content Similarity = {cos_sim*100:.2f}%"
                                pp_list.append((file1, file2))
                        else:
                            msg = f"\nLevel 2: Potential Plagiarism between {file1} and {file2} with UDP = {similarity*100:.2f}%"
                            pp_list.append((file1, file2))
                        st.write(msg)
                        result_log.append(msg)
                    else:
                        text1, text2 = text_list[i], text_list[j]
                        if text1 and text2:
                            emb1, emb2 = model.encode(text1), model.encode(text2)
                            cos_sim = util.cos_sim(emb1, emb2).item()
                            if cos_sim >= 0.85:
                                msg = f"\nLevel 3: Complete Plagiarism between {file1} and {file2}"
                                cp_list.append((file1, file2))
                            elif cos_sim >= 0.75:
                                msg = f"\nLevel 3: Potential Plagiarism between {file1} and {file2} with similarity = {cos_sim*100:.2f}%"
                                pp_list.append((file1, file2))
                            else:
                                continue
                        else:
                            msg = f"\nUnable to load text for {file1} and {file2}"
                        st.write(msg)
                        result_log.append(msg)

            if checkbok:
                for i in range(len(submissions)):
                    if submissions[i] in excluded_docs: continue
                    for j in range(i + 1, len(submissions)):
                        text1, text2 = text_list[i], text_list[j]
                        if text1 and text2:
                            paraphrased = compare_text_similarity(text1, text2)
                            paraphrased = extract_similarity_value(paraphrased)
                            if paraphrased:
                                msg = f"\nLevel 4: Potential Plagiarism (Paraphrased) between {submissions[i].name} and {submissions[j].name}"
                                level4_list.append((submissions[i].name, submissions[j].name))
                                st.write(msg)
                                result_log.append(msg)
                        else:
                            msg = f"\nUnable to process paraphrased text for {submissions[i].name} and {submissions[j].name}"
                            st.write(msg)
                            result_log.append(msg)

        # Final summary section
        if not cp_list and not pp_list and not level4_list:
            msg = "✅ No Plagiarism Detected! All documents are unique."
            st.success(msg)
            result_log.append(msg)
        else:
            with st.expander("Complete Plagiarism Pairs"):
                st.write(cp_list)
            with st.expander("Potential Plagiarism Pairs"):
                st.write(pp_list)
            if checkbok:
                with st.expander("Paraphrased Plagiarism Pairs"):
                    st.write(level4_list)

        return "\n".join(result_log)
