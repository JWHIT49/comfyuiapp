import React, { useRef, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as ImagePicker from 'expo-image-picker';

import { createJob, jobImageUrl, pollJob } from './src/api';
import { PROMPT_SUGGESTIONS } from './src/config';

export default function App() {
  const [imageUri, setImageUri] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('idle'); // idle | working | done | error
  const [progress, setProgress] = useState(0);
  const [resultUri, setResultUri] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const abortRef = useRef(null);

  const busy = status === 'working';

  async function pickImage() {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      setErrorMsg('Photo library permission is required to pick an image.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      resetResult();
    }
  }

  async function takePhoto() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      setErrorMsg('Camera permission is required to take a photo.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ quality: 1 });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      resetResult();
    }
  }

  function resetResult() {
    setResultUri(null);
    setStatus('idle');
    setProgress(0);
    setErrorMsg(null);
  }

  async function runEdit() {
    if (!imageUri || !prompt.trim()) {
      setErrorMsg('Pick an image and type an instruction first.');
      return;
    }
    setStatus('working');
    setProgress(0);
    setErrorMsg(null);
    setResultUri(null);

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const job = await createJob(imageUri, prompt.trim());
      await pollJob(job.job_id, setProgress, controller.signal);
      setResultUri(jobImageUrl(job.job_id));
      setStatus('done');
    } catch (err) {
      if (err.message === 'Cancelled') {
        setStatus('idle');
      } else {
        setErrorMsg(err.message);
        setStatus('error');
      }
    } finally {
      abortRef.current = null;
    }
  }

  function cancel() {
    abortRef.current?.abort();
  }

  return (
    <View style={styles.root}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>ComfyUI Image Edit</Text>
        <Text style={styles.subtitle}>
          Pick a photo, describe a change, let Flux Kontext do the rest.
        </Text>

        {/* Image preview / picker */}
        <View style={styles.previewBox}>
          {imageUri ? (
            <Image source={{ uri: imageUri }} style={styles.preview} resizeMode="cover" />
          ) : (
            <Text style={styles.previewHint}>No image selected</Text>
          )}
        </View>

        <View style={styles.row}>
          <Pressable style={[styles.btn, styles.btnGhost]} onPress={pickImage} disabled={busy}>
            <Text style={styles.btnGhostText}>Choose Photo</Text>
          </Pressable>
          <Pressable style={[styles.btn, styles.btnGhost]} onPress={takePhoto} disabled={busy}>
            <Text style={styles.btnGhostText}>Take Photo</Text>
          </Pressable>
        </View>

        {/* Prompt input */}
        <TextInput
          style={styles.input}
          placeholder='e.g. "Give him a hat"'
          placeholderTextColor="#6b7280"
          value={prompt}
          onChangeText={setPrompt}
          editable={!busy}
          multiline
        />

        {/* Suggestion chips */}
        <View style={styles.chips}>
          {PROMPT_SUGGESTIONS.map((s) => (
            <Pressable
              key={s}
              style={styles.chip}
              onPress={() => setPrompt(s)}
              disabled={busy}
            >
              <Text style={styles.chipText}>{s}</Text>
            </Pressable>
          ))}
        </View>

        {/* Primary action */}
        {busy ? (
          <Pressable style={[styles.btn, styles.btnCancel]} onPress={cancel}>
            <Text style={styles.btnText}>Cancel</Text>
          </Pressable>
        ) : (
          <Pressable style={[styles.btn, styles.btnPrimary]} onPress={runEdit}>
            <Text style={styles.btnText}>Apply Edit</Text>
          </Pressable>
        )}

        {/* Progress / error / result */}
        {busy && (
          <View style={styles.statusBox}>
            <ActivityIndicator color="#8b5cf6" />
            <Text style={styles.statusText}>Editing… {progress}%</Text>
          </View>
        )}
        {errorMsg && <Text style={styles.error}>{errorMsg}</Text>}

        {resultUri && (
          <View style={styles.resultBox}>
            <Text style={styles.resultLabel}>Result</Text>
            <Image source={{ uri: resultUri }} style={styles.result} resizeMode="contain" />
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0b1020' },
  content: { padding: 20, paddingTop: 64, paddingBottom: 48 },
  title: { color: '#f9fafb', fontSize: 28, fontWeight: '700' },
  subtitle: { color: '#9ca3af', fontSize: 14, marginTop: 6, marginBottom: 20 },
  previewBox: {
    height: 280,
    borderRadius: 16,
    backgroundColor: '#111827',
    borderWidth: 1,
    borderColor: '#1f2937',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  preview: { width: '100%', height: '100%' },
  previewHint: { color: '#6b7280' },
  row: { flexDirection: 'row', gap: 12, marginTop: 12 },
  btn: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnGhost: { backgroundColor: '#1f2937' },
  btnGhostText: { color: '#e5e7eb', fontWeight: '600' },
  btnPrimary: { backgroundColor: '#8b5cf6', marginTop: 16 },
  btnCancel: { backgroundColor: '#ef4444', marginTop: 16 },
  btnText: { color: '#ffffff', fontWeight: '700', fontSize: 16 },
  input: {
    marginTop: 16,
    minHeight: 56,
    backgroundColor: '#111827',
    borderColor: '#1f2937',
    borderWidth: 1,
    borderRadius: 12,
    color: '#f9fafb',
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
  },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 },
  chip: {
    backgroundColor: '#171f33',
    borderColor: '#2a3550',
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  chipText: { color: '#c4b5fd', fontSize: 13 },
  statusBox: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 18 },
  statusText: { color: '#d1d5db', fontSize: 15 },
  error: { color: '#fca5a5', marginTop: 16, fontSize: 14 },
  resultBox: { marginTop: 24 },
  resultLabel: { color: '#9ca3af', fontSize: 13, marginBottom: 8, textTransform: 'uppercase' },
  result: {
    width: '100%',
    height: 360,
    borderRadius: 16,
    backgroundColor: '#111827',
  },
});
