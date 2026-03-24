import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function Layout() {
  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: "#0f0f1a" },
        headerTintColor: "#fff",
        tabBarStyle: { backgroundColor: "#0f0f1a", borderTopColor: "#1a1a2e" },
        tabBarActiveTintColor: "#6c63ff",
        tabBarInactiveTintColor: "#555",
      }}
    >
      <Tabs.Screen
        name="(tabs)/index"
        options={{
          title: "Watchlist",
          tabBarIcon: ({ color, size }) => <Ionicons name="list" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="(tabs)/add"
        options={{
          title: "Add Alert",
          tabBarIcon: ({ color, size }) => <Ionicons name="add-circle-outline" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="(tabs)/chat"
        options={{
          title: "Assistant",
          tabBarIcon: ({ color, size }) => <Ionicons name="chatbubble-outline" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
