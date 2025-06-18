import React, { useState } from 'react'
import { SafeAreaView, View, Button, ScrollView, Text, StyleSheet } from 'react-native'
import axios from 'axios'

export default function App() {
  const [leagueInfo, setLeagueInfo] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchLeague = async () => {
    setLoading(true)
    try {
      // replace with your real backend URL
      const response = await axios.get(
        'https://drafter.michaelspollard.com/leagueinfo',
        { params: { league_id: '102423' } }
      )
      setLeagueInfo(response.data)
    } catch (error) {
      console.error('Failed to fetch league info:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.buttonContainer}>
        <Button
          title={loading ? 'Loading…' : 'Load League Info'}
          onPress={fetchLeague}
          disabled={loading}
        />
      </View>
      {leagueInfo && (
        <ScrollView style={styles.infoContainer}>
          <Text style={styles.infoText}>
            {JSON.stringify(leagueInfo, null, 2)}
          </Text>
        </ScrollView>
      )}
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  buttonContainer: { padding: 16 },
  infoContainer: { padding: 12 },
  infoText: { fontFamily: 'monospace', fontSize: 14 }
})

