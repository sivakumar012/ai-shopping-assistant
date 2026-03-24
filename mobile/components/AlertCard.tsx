import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, Linking } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import type { Alert } from "../services/api";

type Props = {
  alert: Alert;
  onDelete: (id: number) => void;
  onToggle: (id: number, active: boolean) => void;
  onReset: (id: number) => void;
};

export function AlertCard({ alert, onDelete, onToggle, onReset }: Props) {
  const priceHit = alert.current_price !== null && alert.current_price <= alert.target_price;

  const badge = alert.notified
    ? { label: "Notified", color: "#27ae60" }
    : !alert.is_active
    ? { label: "Paused", color: "#7f8c8d" }
    : { label: "Watching", color: "#6c63ff" };

  return (
    <View style={styles.card}>
      <TouchableOpacity onPress={() => Linking.openURL(alert.product_url)}>
        <Text style={styles.name} numberOfLines={2}>{alert.product_name}</Text>
      </TouchableOpacity>

      <View style={styles.prices}>
        <View>
          <Text style={styles.label}>Target</Text>
          <Text style={styles.price}>₹{alert.target_price.toLocaleString("en-IN")}</Text>
        </View>
        <View>
          <Text style={styles.label}>Current</Text>
          <Text style={[styles.price, priceHit && styles.priceHit]}>
            {alert.current_price ? `₹${alert.current_price.toLocaleString("en-IN")}` : "—"}
          </Text>
        </View>
        <View style={[styles.badge, { backgroundColor: badge.color }]}>
          <Text style={styles.badgeText}>{badge.label}</Text>
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity onPress={() => onToggle(alert.id, !alert.is_active)} style={styles.btn}>
          <Ionicons name={alert.is_active ? "pause" : "play"} size={16} color="#aaa" />
          <Text style={styles.btnText}>{alert.is_active ? "Pause" : "Resume"}</Text>
        </TouchableOpacity>

        {alert.notified && (
          <TouchableOpacity onPress={() => onReset(alert.id)} style={styles.btn}>
            <Ionicons name="refresh" size={16} color="#aaa" />
            <Text style={styles.btnText}>Re-watch</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity onPress={() => onDelete(alert.id)} style={[styles.btn, styles.btnDanger]}>
          <Ionicons name="trash-outline" size={16} color="#e74c3c" />
          <Text style={[styles.btnText, { color: "#e74c3c" }]}>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  name: { color: "#fff", fontSize: 15, fontWeight: "600", marginBottom: 12 },
  prices: { flexDirection: "row", alignItems: "center", gap: 16, marginBottom: 12 },
  label: { color: "#888", fontSize: 11, marginBottom: 2 },
  price: { color: "#fff", fontSize: 16, fontWeight: "700" },
  priceHit: { color: "#27ae60" },
  badge: { marginLeft: "auto", paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  badgeText: { color: "#fff", fontSize: 11, fontWeight: "600" },
  actions: { flexDirection: "row", gap: 8 },
  btn: { flexDirection: "row", alignItems: "center", gap: 4, paddingVertical: 6, paddingHorizontal: 10, borderRadius: 8, backgroundColor: "#0f0f1a" },
  btnDanger: { marginLeft: "auto" },
  btnText: { color: "#aaa", fontSize: 13 },
});
