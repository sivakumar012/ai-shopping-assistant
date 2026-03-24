import React, { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { api } from "../../services/api";
import { Toast } from "../../components/Toast";

export default function AddAlertScreen() {
  const [form, setForm] = useState({
    product_name: "",
    product_url: "",
    target_price: "",
    whatsapp_number: "",
  });
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ message: "", isError: false, visible: false });

  const showToast = (message: string, isError = false) => {
    setToast({ message, isError, visible: true });
    setTimeout(() => setToast((t) => ({ ...t, visible: false })), 3200);
  };

  const set = (key: keyof typeof form) => (val: string) =>
    setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async () => {
    const price = parseFloat(form.target_price);
    if (!form.product_name.trim()) return showToast("Product name is required", true);
    if (!form.product_url.trim()) return showToast("Product URL is required", true);
    if (isNaN(price) || price <= 0) return showToast("Enter a valid target price", true);
    if (!form.whatsapp_number.trim()) return showToast("WhatsApp number is required", true);

    setLoading(true);
    try {
      await api.createAlert({
        product_name: form.product_name.trim(),
        product_url: form.product_url.trim(),
        target_price: price,
        whatsapp_number: form.whatsapp_number.trim(),
      });
      showToast("Alert added");
      setForm({ product_name: "", product_url: "", target_price: "", whatsapp_number: "" });
      setTimeout(() => router.replace("/(tabs)/"), 1000);
    } catch (e: any) {
      showToast(e.message, true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["bottom"]}>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <Text style={styles.hint}>Paste an Amazon product URL and set your target price. We'll alert you on WhatsApp when it drops.</Text>

          <Text style={styles.label}>Product Name</Text>
          <TextInput style={styles.input} placeholder="e.g. iPhone 15" placeholderTextColor="#555" value={form.product_name} onChangeText={set("product_name")} />

          <Text style={styles.label}>Amazon URL</Text>
          <TextInput style={styles.input} placeholder="https://www.amazon.in/..." placeholderTextColor="#555" value={form.product_url} onChangeText={set("product_url")} autoCapitalize="none" keyboardType="url" />

          <Text style={styles.label}>Target Price (₹)</Text>
          <TextInput style={styles.input} placeholder="e.g. 60000" placeholderTextColor="#555" value={form.target_price} onChangeText={set("target_price")} keyboardType="numeric" />

          <Text style={styles.label}>WhatsApp Number</Text>
          <TextInput style={styles.input} placeholder="+919876543210" placeholderTextColor="#555" value={form.whatsapp_number} onChangeText={set("whatsapp_number")} keyboardType="phone-pad" />

          <TouchableOpacity style={[styles.btn, loading && styles.btnDisabled]} onPress={handleSubmit} disabled={loading}>
            <Text style={styles.btnText}>{loading ? "Adding..." : "Add Alert"}</Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
      <Toast {...toast} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f1a" },
  scroll: { padding: 20, paddingBottom: 40 },
  hint: { color: "#888", fontSize: 14, lineHeight: 20, marginBottom: 24 },
  label: { color: "#aaa", fontSize: 13, marginBottom: 6, marginTop: 16 },
  input: { backgroundColor: "#1a1a2e", color: "#fff", borderRadius: 10, padding: 14, fontSize: 15 },
  btn: { backgroundColor: "#6c63ff", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 32 },
  btnDisabled: { opacity: 0.5 },
  btnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
});
