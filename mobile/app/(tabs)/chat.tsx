import React, { useRef, useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { API_BASE } from "../../constants/config";

type Message = { id: string; role: "user" | "assistant"; text: string };

const SUGGESTIONS = [
  "Running shoes under ₹5000",
  "Gaming laptop under ₹60000",
  "Wireless earbuds under ₹2000",
];

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "0", role: "assistant", text: "Hi! Tell me what you're looking for and I'll find the best options for you." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef<FlatList>(null);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", text: text.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text.trim() }),
      });
      const data = await res.json();
      const reply: Message = { id: (Date.now() + 1).toString(), role: "assistant", text: data.reply || "Sorry, I couldn't process that." };
      setMessages((m) => [...m, reply]);
    } catch {
      setMessages((m) => [...m, { id: (Date.now() + 1).toString(), role: "assistant", text: "Something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["bottom"]}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined} keyboardVerticalOffset={90}>
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(m) => m.id}
          contentContainerStyle={styles.list}
          onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
          renderItem={({ item }) => (
            <View style={[styles.bubble, item.role === "user" ? styles.userBubble : styles.aiBubble]}>
              <Text style={[styles.bubbleText, item.role === "user" && styles.userText]}>{item.text}</Text>
            </View>
          )}
          ListFooterComponent={
            loading ? (
              <View style={styles.aiBubble}>
                <Text style={styles.bubbleText}>Thinking...</Text>
              </View>
            ) : messages.length === 1 ? (
              <View style={styles.suggestions}>
                {SUGGESTIONS.map((s) => (
                  <TouchableOpacity key={s} style={styles.chip} onPress={() => send(s)}>
                    <Text style={styles.chipText}>{s}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : null
          }
        />

        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder="What are you looking for?"
            placeholderTextColor="#555"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={() => send(input)}
            returnKeyType="send"
            editable={!loading}
          />
          <TouchableOpacity style={[styles.sendBtn, (!input.trim() || loading) && styles.sendDisabled]} onPress={() => send(input)} disabled={!input.trim() || loading}>
            <Ionicons name="send" size={18} color="#fff" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f1a" },
  list: { padding: 16, paddingBottom: 8, gap: 8 },
  bubble: { maxWidth: "80%", borderRadius: 16, padding: 12 },
  aiBubble: { backgroundColor: "#1a1a2e", alignSelf: "flex-start" },
  userBubble: { backgroundColor: "#6c63ff", alignSelf: "flex-end" },
  bubbleText: { color: "#ccc", fontSize: 14, lineHeight: 20 },
  userText: { color: "#fff" },
  suggestions: { gap: 8, marginTop: 8 },
  chip: { backgroundColor: "#1a1a2e", borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, alignSelf: "flex-start" },
  chipText: { color: "#6c63ff", fontSize: 13 },
  inputRow: { flexDirection: "row", padding: 12, gap: 8, borderTopWidth: 1, borderTopColor: "#1a1a2e" },
  input: { flex: 1, backgroundColor: "#1a1a2e", color: "#fff", borderRadius: 24, paddingHorizontal: 16, paddingVertical: 10, fontSize: 15 },
  sendBtn: { backgroundColor: "#6c63ff", borderRadius: 24, width: 44, height: 44, justifyContent: "center", alignItems: "center" },
  sendDisabled: { opacity: 0.4 },
});
