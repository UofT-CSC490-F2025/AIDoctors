# CloudFront Distribution for Frontend
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${local.name}-frontend-oac"
  description                       = "Origin Access Control for S3 Frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for ${local.name} frontend"
  default_root_object = "index.html"
  price_class         = "PriceClass_100" # Use only North America and Europe edge locations

  # Origin #1: S3 bucket for frontend static files
  origin {
    domain_name              = module.s3_frontend.s3_bucket_bucket_regional_domain_name
    origin_id                = "S3-${module.s3_frontend.s3_bucket_id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  # Origin #2: ALB for backend API
  origin {
    domain_name = module.alb.dns_name
    origin_id   = "ALB-${local.name}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${module.s3_frontend.s3_bucket_id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  # Cache behavior for API requests - route to ALB
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${local.name}"

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Accept", "Content-Type"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = true
  }

  # Cache behavior for static assets (JS, CSS, images)
  ordered_cache_behavior {
    path_pattern     = "/_next/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${module.s3_frontend.s3_bucket_id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 31536000
    default_ttl            = 31536000
    max_ttl                = 31536000
    compress               = true
  }

  # Custom error response for SPA routing
  # For Next.js static export, redirect 404s to root index.html for client-side routing
  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Use CloudFront's default SSL certificate
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name    = "${local.name}-frontend-cdn"
    Purpose = "Frontend CDN"
  }
}

# Update S3 bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "frontend_cloudfront" {
  bucket = module.s3_frontend.s3_bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${module.s3_frontend.s3_bucket_arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}
