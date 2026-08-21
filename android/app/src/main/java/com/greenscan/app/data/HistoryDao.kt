package com.greenscan.app.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.greenscan.app.model.HistoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {

    @Query("SELECT * FROM scan_history ORDER BY id DESC")
    fun getAllScans(): Flow<List<HistoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertScan(scan: HistoryEntity): Long

    @Query("DELETE FROM scan_history")
    suspend fun clearHistory()
}
