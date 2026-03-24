import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { api, Alert } from "../../services/api";
import { AlertCard } from "../../components/AlertCard";
import { Toast } from "../../components/Toast";

export default function WatchlistScreen() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [toast, setToast] = useState({ message: "", isError: false, visible: false });

  const showToast = (message: string, isError = false) => {
    setToast({ message, isError, visible: true });
    setTimeout(() => setToast((t) => ({ ...t, visible: false })), 3200);
  };

  const load = useCallback(async () => {
    try {
      const data = await api.listAlerts();
      setAlerts(data);
    } catch (e: any) {
      showToast(e.message, true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async (id: number) => {
    try {
      await api.deleteAlert(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      showToast("Alert removed");
    } catch (e: any) {
      showToast(e.message, true);
    }
  };

  const handleToggle = async (id: number, active: boolean) => {
    try {
      const updated = await api.updateAlert(id, { is_active: active });
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (e: any) {
      showToast(e.message, true);
    }
  };

  const handleReset = async (id: number) => {
    try {
      const updated = await api.resetAlert(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
      showToast("Re-watching product");
    } catch (e: any) {
      showToast(e.message, true);
    }
  };

  const handleCheckNow = async () => {
    try {
      await api.triggerCheck();
      showToast("Price check triggered");
      setTimeout(load, 3000);
    } catch (e: any) {
      showToast(e.message, true);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#6c63ff" size="large" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["bottom"]}>
      <FlatList
        data={alerts}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <AlertCard
            alert={item}
            onDelete={handleDelete}
            onToggle={handleToggle}
            onReset={handleReset}
          />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor="#6c63ff" />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="pricetag-outline" size={48} color="#333" />
            <Text style={styles.emptyText}>No alerts yet.{"\n"}Tap + to add one.</Text>
          </View>
        }
        ListFooterComponent={
          alerts.length > 0 ? (
            <TouchableOpacity style={styles.checkBtn} onPress={handleCheckNow}>
              <Ionicons name="refresh" size={16} color="#6c63ff" />
              <Text style={styles.checkBtnText}>Check Prices Now</Text>
            </TouchableOpacity>
          ) : null
        }
      />
      <Toast {...toast} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f1a" },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#0f0f1a" },
  list: { padding: 16, paddingBottom: 32 },
  empty: { alignItems: "center", marginTop: 80, gap: 12 },
  emptyText: { color: "#555", fontSize: 15, textAlign: "center", lineHeight: 22 },
  checkBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, padding: 14, borderRadius: 12, borderWidth: 1, borderColor: "#6c63ff", marginTop: 8 },
  checkBtnText: { color: "#6c63ff", fontSize: 14, fontWeight: "600" },
});
