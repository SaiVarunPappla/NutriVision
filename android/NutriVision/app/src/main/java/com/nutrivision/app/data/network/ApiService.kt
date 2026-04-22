package com.nutrivision.app.data.network

import com.nutrivision.app.data.model.HistoryResponse
import com.nutrivision.app.data.model.UserProfile
import com.nutrivision.app.data.model.UserProfileUpdate
import com.nutrivision.app.data.model.TextScanRequest
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.data.model.ChatRequest
import com.nutrivision.app.data.model.ChatResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    @POST("api/v1/scan/text")
    suspend fun scanText(@Body request: TextScanRequest): Response<ScanResponse>

    @Multipart
    @POST("api/v1/scan/image")
    suspend fun scanImage(
        @Part image: MultipartBody.Part,
        @Part("user_id") userId: RequestBody,
        @Part("product_name") productName: RequestBody? = null
    ): Response<ScanResponse>

    @GET("api/v1/history/{user_id}")
    suspend fun getHistory(@Path("user_id") userId: String): Response<HistoryResponse>

    @GET("api/v1/user/{user_id}")
    suspend fun getUserProfile(@Path("user_id") userId: String): Response<UserProfile>

    @PUT("api/v1/user/{user_id}")
    suspend fun updateUserProfile(@Path("user_id") userId: String, @Body update: UserProfileUpdate): Response<UserProfile>

    @POST("api/v1/chat")
    suspend fun askChat(@Body request: ChatRequest): Response<ChatResponse>
}
